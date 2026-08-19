from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import logging
import time

from opportunity_ingestion.bdns import BdnsClient
from opportunity_ingestion.db.session import create_db_engine, session_factory
from opportunity_ingestion.repositories.grant_calls import upsert_core_grant_call
from opportunity_ingestion.repositories.raw_grant_calls import upsert_raw_grant_call
from opportunity_ingestion.transformers.grant_call import raw_payload, transform_call

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IngestionSummary:
    fetched: int = 0
    new: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0


def ingest_calls(
    *,
    date_from: date,
    date_to: date,
    limit: int,
    dry_run: bool = False,
) -> IngestionSummary:
    if limit < 1:
        raise ValueError("limit must be positive")
    if date_to < date_from:
        raise ValueError("date_to must not be before date_from")

    summary = IngestionSummary()
    started = time.perf_counter()
    engine = create_db_engine() if not dry_run else None
    factory = session_factory(engine) if engine is not None else None
    try:
        with BdnsClient() as client:
            logger.info("batch_started date_from=%s date_to=%s limit=%s dry_run=%s", date_from, date_to, limit, dry_run)
            summaries = []
            for page in client.iter_search_calls(
                max_pages=(limit + client.config.page_size - 1) // client.config.page_size,
                page_size=min(limit, client.config.page_size),
                fechaDesde=date_from.strftime("%d/%m/%Y"),
                fechaHasta=date_to.strftime("%d/%m/%Y"),
            ):
                summaries.extend(page.content[: max(0, limit - len(summaries))])
                if len(summaries) >= limit:
                    break

            for item in summaries:
                code = item.numero_convocatoria
                try:
                    logger.info("grant_ingestion_started bdns_code=%s", code)
                    detail = client.get_call_detail(code)
                    data = transform_call(detail)
                    payload = raw_payload(detail)
                    summary.fetched += 1
                    if dry_run:
                        logger.info("grant_validated bdns_code=%s", code)
                        summary.new += 1
                        continue

                    assert factory is not None
                    with factory() as session:
                        with session.begin():
                            raw_row, raw_changed = upsert_raw_grant_call(
                                session,
                                bdns_code=code,
                                payload=payload,
                                source_endpoint=f"{client.config.base_url}/convocatorias",
                            )
                            if raw_changed:
                                logger.info("grant_raw_created_or_changed bdns_code=%s", code)
                            else:
                                logger.info("grant_raw_unchanged bdns_code=%s", code)
                            _, core_new = upsert_core_grant_call(session, data=data, raw_id=raw_row.id)
                            logger.info("grant_core_upserted bdns_code=%s", code)
                    if core_new:
                        summary.new += 1
                    elif raw_changed:
                        summary.updated += 1
                    else:
                        summary.unchanged += 1
                except Exception:
                    summary.failed += 1
                    logger.exception("grant_ingestion_failed bdns_code=%s", code)
    finally:
        if engine is not None:
            engine.dispose()
    logger.info("batch_completed fetched=%s new=%s updated=%s unchanged=%s failed=%s duration_ms=%.0f", summary.fetched, summary.new, summary.updated, summary.unchanged, summary.failed, (time.perf_counter() - started) * 1000)
    return summary
