from __future__ import annotations

from datetime import date, datetime, timezone
import logging
import re

from sqlalchemy import exists, func, or_, select, text, update
from sqlalchemy.orm import Session

from opportunity_ingestion.db.models import GrantCall, IngestionFailure, IngestionRun, RawBdnsGrantCall


ACTIVE_STATUSES = ("pending", "running", "failed", "interrupted")
logger = logging.getLogger(__name__)


def sanitize_error(error: BaseException, *, limit: int = 1000) -> str:
    return _sanitize_text(f"{type(error).__name__}: {error}", limit=limit)


def _sanitize_text(value: str, *, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"(?i)(password|token|secret|database_url)=[^ ]+", r"\1=[REDACTED]", value)
    return value[:limit]


def database_error_details(error: BaseException) -> dict[str, str | None]:
    """Return safe DBAPI diagnostics when an error exposes PostgreSQL details."""
    original = getattr(error, "orig", error)
    diagnostic = getattr(original, "diag", None)

    def value(*names: str) -> str | None:
        for name in names:
            candidate = getattr(original, name, None) or getattr(diagnostic, name, None)
            if candidate:
                return _sanitize_text(str(candidate), limit=500)
        return None

    return {
        "sqlstate": value("sqlstate", "pgcode"),
        "constraint": value("constraint_name"),
        "detail": value("message_detail", "detail"),
    }


def lock_key(source: str, date_from: date, date_to: date) -> str:
    return f"opportunity-intel:{source}:{date_from.isoformat()}:{date_to.isoformat()}"


def try_acquire_window_lock(connection, key: str) -> bool:
    """Acquire a session-level lock on an AUTOCOMMIT connection."""
    return bool(connection.execute(text("SELECT pg_try_advisory_lock(hashtextextended(:key, 0))"), {"key": key}).scalar_one())


def release_window_lock(connection, key: str) -> None:
    """Release a session-level lock without masking the window's original error."""
    try:
        connection.execute(text("SELECT pg_advisory_unlock(hashtextextended(:key, 0))"), {"key": key})
    except Exception as error:
        logger.warning(
            "window_lock_release_failed key=%s error_type=%s error=%s",
            key,
            type(error).__name__,
            sanitize_error(error),
        )


def latest_run(session: Session, *, source: str, date_from: date, date_to: date) -> IngestionRun | None:
    return session.scalar(
        select(IngestionRun)
        .where(IngestionRun.source == source, IngestionRun.date_from == date_from, IngestionRun.date_to == date_to)
        .order_by(IngestionRun.id.desc())
        .limit(1)
    )


def create_run(session: Session, *, source: str, date_from: date, date_to: date) -> IngestionRun:
    run = IngestionRun(source=source, date_from=date_from, date_to=date_to, status="running")
    session.add(run)
    session.flush()
    return run


def update_run(session: Session, run_id: int, **values: object) -> None:
    session.execute(update(IngestionRun).where(IngestionRun.id == run_id).values(**values))


def record_failure(session: Session, *, run_id: int, bdns_code: str, stage: str, error: BaseException) -> IngestionFailure:
    error_type = type(error).__name__
    existing = session.scalar(
        select(IngestionFailure).where(
            IngestionFailure.ingestion_run_id == run_id,
            IngestionFailure.bdns_code == bdns_code,
            IngestionFailure.stage == stage,
            IngestionFailure.error_type == error_type,
            IngestionFailure.resolved_at.is_(None),
        )
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.attempts += 1
        existing.last_attempt_at = now
        existing.error_message = sanitize_error(error)
        return existing
    failure = IngestionFailure(
        ingestion_run_id=run_id,
        bdns_code=bdns_code,
        stage=stage,
        error_type=error_type,
        error_message=sanitize_error(error),
        attempts=1,
        first_failed_at=now,
        last_attempt_at=now,
    )
    session.add(failure)
    session.flush()
    return failure


def unresolved_failures(session: Session, run_id: int) -> list[IngestionFailure]:
    return list(session.scalars(select(IngestionFailure).where(IngestionFailure.ingestion_run_id == run_id, IngestionFailure.resolved_at.is_(None)).order_by(IngestionFailure.id)))


def resolve_failure(session: Session, failure: IngestionFailure) -> None:
    failure.resolved_at = datetime.now(timezone.utc)


def resolve_failures_for_code(session: Session, bdns_code: str) -> int:
    """Resolve every pending failure for a code after successful ingestion.

    Failures are deliberately retained as an audit trail. A later successful
    ingestion is the evidence that makes all earlier failures for that code
    resolved, including failures from older runs.
    """
    result = session.execute(
        update(IngestionFailure)
        .where(IngestionFailure.bdns_code == bdns_code, IngestionFailure.resolved_at.is_(None))
        .values(resolved_at=datetime.now(timezone.utc))
    )
    return result.rowcount or 0


def unresolved_failure_count(session: Session) -> int:
    """Count every operational failure that has not been explicitly resolved."""
    return session.scalar(
        select(func.count()).select_from(IngestionFailure).where(IngestionFailure.resolved_at.is_(None))
    ) or 0


def _successful_ingestion_exists():
    """Return evidence of a later RAW/CORE observation for the failed code."""
    return exists(
        select(GrantCall.id)
        .join(RawBdnsGrantCall, GrantCall.raw_id == RawBdnsGrantCall.id)
        .where(
            GrantCall.bdns_code == IngestionFailure.bdns_code,
            or_(
                GrantCall.last_seen_at > IngestionFailure.last_attempt_at,
                RawBdnsGrantCall.last_seen_at > IngestionFailure.last_attempt_at,
            ),
        )
    )


def reconcilable_failure_count(session: Session) -> int:
    """Count pending failures with demonstrable later RAW/CORE ingestion."""
    return session.scalar(
        select(func.count())
        .select_from(IngestionFailure)
        .where(IngestionFailure.resolved_at.is_(None), _successful_ingestion_exists())
    ) or 0


def reconcile_failures_with_successful_ingestion(session: Session) -> int:
    """Resolve only failures followed by a later successful RAW/CORE observation."""
    result = session.execute(
        update(IngestionFailure)
        .where(IngestionFailure.resolved_at.is_(None), _successful_ingestion_exists())
        .values(resolved_at=datetime.now(timezone.utc))
    )
    return result.rowcount or 0
