from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from opportunity_ingestion.db.models import RawBdnsGrantCall


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def upsert_raw_grant_call(
    session: Session,
    *,
    bdns_code: str,
    payload: dict[str, Any],
    source_endpoint: str,
    observed_at: datetime | None = None,
) -> tuple[RawBdnsGrantCall, bool]:
    now = observed_at or datetime.now(timezone.utc)
    payload_hash = canonical_payload_hash(payload)
    row = session.scalar(select(RawBdnsGrantCall).where(RawBdnsGrantCall.bdns_code == bdns_code))
    if row is None:
        row = RawBdnsGrantCall(
            bdns_code=bdns_code,
            payload=payload,
            payload_hash=payload_hash,
            source_endpoint=source_endpoint,
            source_retrieved_at=now,
            first_seen_at=now,
            last_seen_at=now,
        )
        session.add(row)
        session.flush()
        return row, True
    changed = row.payload_hash != payload_hash
    if changed:
        row.payload = payload
        row.payload_hash = payload_hash
        row.source_endpoint = source_endpoint
        row.source_retrieved_at = now
    row.last_seen_at = now
    session.flush()
    return row, changed

