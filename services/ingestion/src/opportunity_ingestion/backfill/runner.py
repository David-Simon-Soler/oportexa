from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import logging
import signal
import time

from sqlalchemy import select

from opportunity_ingestion.bdns import BdnsClient
from opportunity_ingestion.db.models import IngestionFailure, IngestionRun
from opportunity_ingestion.db.session import create_db_engine, session_factory
from opportunity_ingestion.etl import ingest_one

from .ops import (
    create_run,
    latest_run,
    lock_key,
    record_failure,
    release_window_lock,
    resolve_failure,
    sanitize_error,
    try_acquire_window_lock,
    unresolved_failures,
    update_run,
)
from .windows import DateWindow, WindowKind, generate_windows

logger = logging.getLogger(__name__)
SOURCE = "bdns"
DEFAULT_PAGE_SIZE = 100


class BackfillInterrupted(Exception):
    pass


@dataclass(slots=True)
class BackfillResult:
    windows: int = 0
    skipped: int = 0
    pages: int = 0
    fetched: int = 0
    succeeded: int = 0
    failed: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    requests_approx: int = 0
    duration_seconds: float = 0.0


def _set_status(engine, run_id: int, status: str, *, error_summary: str | None = None) -> None:
    with session_factory(engine)() as session:
        with session.begin():
            values: dict[str, object] = {"status": status}
            if status in {"completed", "failed", "interrupted"}:
                values["completed_at"] = datetime.now(timezone.utc)
            if error_summary is not None:
                values["error_summary"] = error_summary
            update_run(session, run_id, **values)


def _update_page_checkpoint(engine, run_id: int, *, page: int, fetched: int, succeeded: int, failed: int) -> None:
    with session_factory(engine)() as session:
        with session.begin():
            run = session.get(IngestionRun, run_id)
            if run is None:
                raise RuntimeError(f"ingestion run {run_id} not found")
            update_run(
                session,
                run_id,
                last_page=page,
                fetched=run.fetched + fetched,
                succeeded=run.succeeded + succeeded,
                failed=run.failed + failed,
                status="running",
            )


def _retry_run_failures(engine, run_id: int, client: BdnsClient, *, result: BackfillResult) -> int:
    with session_factory(engine)() as session:
        failures = unresolved_failures(session, run_id)
    resolved = 0
    for failure in failures:
        try:
            outcome = ingest_one(factory=session_factory(engine), client=client, bdns_code=failure.bdns_code)
        except Exception as error:  # individual failures must not stop the window
            with session_factory(engine)() as session:
                with session.begin():
                    record_failure(session, run_id=run_id, bdns_code=failure.bdns_code, stage=failure.stage, error=error)
            result.failed += 1
            continue
        with session_factory(engine)() as session:
            with session.begin():
                current = session.get(IngestionFailure, failure.id)
                if current is not None:
                    resolve_failure(session, current)
        result.fetched += 1
        result.succeeded += 1
        result.requests_approx += 1
        if outcome == "new":
            result.new += 1
        elif outcome == "updated":
            result.updated += 1
        else:
            result.unchanged += 1
        resolved += 1
    return resolved


def _install_signal_handler():
    interrupted = {"value": False}

    def handler(signum, _frame):
        interrupted["value"] = True
        raise BackfillInterrupted(f"received signal {signum}")

    previous = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handler)
    return interrupted, previous


def _restore_signal_handler(previous) -> None:
    signal.signal(signal.SIGINT, previous)


def run_backfill(
    *,
    date_from: date,
    date_to: date,
    window: WindowKind,
    resume: bool = False,
    max_windows: int | None = None,
    limit_per_window: int | None = None,
    retry_failed: bool = False,
    dry_run: bool = False,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> BackfillResult:
    windows = generate_windows(date_from, date_to, window)
    if page_size < 1 or page_size > 500:
        raise ValueError("page_size must be between 1 and 500")
    if limit_per_window is not None and limit_per_window < 1:
        raise ValueError("limit_per_window must be positive")
    selected = windows[:max_windows] if max_windows is not None else windows
    result = BackfillResult(windows=len(selected))
    started = time.perf_counter()
    logger.info("backfill_started windows=%s window=%s dry_run=%s page_size=%s", len(selected), window, dry_run, page_size)
    if dry_run:
        for item in selected:
            logger.info("window_planned date_from=%s date_to=%s", item.date_from, item.date_to)
        result.duration_seconds = time.perf_counter() - started
        logger.info("backfill_completed windows=%s dry_run=true duration_ms=%.0f", len(selected), result.duration_seconds * 1000)
        return result

    engine = create_db_engine()
    interrupted_state, previous_handler = _install_signal_handler()
    try:
        for item in selected:
            key = lock_key(SOURCE, item.date_from, item.date_to)
            with engine.connect() as lock_connection:
                if not try_acquire_window_lock(lock_connection, key):
                    logger.warning("window_skipped_locked date_from=%s date_to=%s", item.date_from, item.date_to)
                    result.skipped += 1
                    continue
                try:
                    _run_window(engine, item, result, resume=resume, retry_failed=retry_failed, limit_per_window=limit_per_window, page_size=page_size)
                finally:
                    release_window_lock(lock_connection, key)
    except BackfillInterrupted as interruption:
        logger.warning("backfill_interrupted reason=%s", sanitize_error(interruption))
        raise
    finally:
        _restore_signal_handler(previous_handler)
        engine.dispose()
        result.duration_seconds = time.perf_counter() - started
    logger.info("backfill_completed windows=%s pages=%s fetched=%s succeeded=%s failed=%s duration_ms=%.0f", result.windows - result.skipped, result.pages, result.fetched, result.succeeded, result.failed, result.duration_seconds * 1000)
    return result


def _run_window(engine, item: DateWindow, result: BackfillResult, *, resume: bool, retry_failed: bool, limit_per_window: int | None, page_size: int) -> None:
    with session_factory(engine)() as session:
        with session.begin():
            existing = latest_run(session, source=SOURCE, date_from=item.date_from, date_to=item.date_to) if resume else None
            if existing is not None and existing.status == "completed":
                result.skipped += 1
                logger.info("window_skipped_completed date_from=%s date_to=%s run=%s", item.date_from, item.date_to, existing.id)
                return
            run = existing or create_run(session, source=SOURCE, date_from=item.date_from, date_to=item.date_to)
            run_id = run.id
            start_page = (run.last_page + 1) if run.last_page is not None else 0
            prior_failed = run.failed
    logger.info("window_started date_from=%s date_to=%s run=%s start_page=%s", item.date_from, item.date_to, run_id, start_page)
    page_count = 0
    window_fetched = 0
    window_started = time.perf_counter()
    try:
        with BdnsClient() as client:
            for page in client.iter_search_calls(
                start_page=start_page,
                page_size=page_size,
                fechaDesde=item.date_from.strftime("%d/%m/%Y"),
                fechaHasta=item.date_to.strftime("%d/%m/%Y"),
            ):
                page_number = page.number if page.number is not None else start_page + page_count
                page_started = time.perf_counter()
                page_fetched = page_succeeded = page_failed = 0
                page_new = page_updated = page_unchanged = 0
                for summary in page.content:
                    if limit_per_window is not None and window_fetched >= limit_per_window:
                        raise BackfillInterrupted("limit_per_window reached")
                    code = summary.numero_convocatoria
                    try:
                        outcome = ingest_one(factory=session_factory(engine), client=client, bdns_code=code)
                        page_fetched += 1
                        window_fetched += 1
                        page_succeeded += 1
                        result.fetched += 1
                        result.succeeded += 1
                        result.requests_approx += 1
                        if outcome == "new": page_new += 1; result.new += 1
                        elif outcome == "updated": page_updated += 1; result.updated += 1
                        else: page_unchanged += 1; result.unchanged += 1
                    except BackfillInterrupted:
                        raise
                    except Exception as error:
                        page_failed += 1
                        result.failed += 1
                        with session_factory(engine)() as failure_session:
                            with failure_session.begin():
                                record_failure(failure_session, run_id=run_id, bdns_code=code, stage="detail", error=error)
                        logger.warning("grant_failed bdns_code=%s error_type=%s", code, type(error).__name__)
                _update_page_checkpoint(engine, run_id, page=page_number, fetched=page_fetched, succeeded=page_succeeded, failed=page_failed)
                page_count += 1
                result.pages += 1
                result.requests_approx += 1
                logger.info("page_completed run=%s page=%s fetched=%s succeeded=%s failed=%s duration_ms=%.0f", run_id, page_number, page_fetched, page_succeeded, page_failed, (time.perf_counter() - page_started) * 1000)
                if page.last is True or not page.content:
                    break
            if retry_failed:
                resolved = _retry_run_failures(engine, run_id, client, result=result)
                if resolved:
                    logger.info("failures_retried run=%s resolved=%s", run_id, resolved)
        with session_factory(engine)() as session:
            unresolved = session.scalar(select(IngestionFailure.id).where(IngestionFailure.ingestion_run_id == run_id, IngestionFailure.resolved_at.is_(None)).limit(1))
        if unresolved is None:
            _set_status(engine, run_id, "completed")
            logger.info("window_completed run=%s duration_ms=%.0f", run_id, (time.perf_counter() - window_started) * 1000)
        else:
            _set_status(engine, run_id, "failed", error_summary=f"unresolved failures remain; prior_failed={prior_failed}")
            logger.warning("window_failed run=%s unresolved_failures=true", run_id)
    except BackfillInterrupted:
        _set_status(engine, run_id, "interrupted", error_summary="interrupted before page confirmation")
        raise
    except Exception as error:
        _set_status(engine, run_id, "failed", error_summary=sanitize_error(error))
        logger.error("window_failed run=%s error_type=%s", run_id, type(error).__name__)
        raise
