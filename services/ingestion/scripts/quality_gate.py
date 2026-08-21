#!/usr/bin/env python3
"""Fail CI when core integrity invariants or unresolved ingestion failures exist."""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select, text

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.db.models import GrantCall, IngestionFailure  # noqa: E402
from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402


def main() -> int:
    engine = create_db_engine()
    violations: list[str] = []
    try:
        with session_factory(engine)() as session:
            core_count = session.scalar(select(func.count()).select_from(GrantCall)) or 0
            duplicate_core = session.scalar(
                select(func.count())
                .select_from(
                    select(GrantCall.bdns_code)
                    .where(GrantCall.bdns_code.is_not(None))
                    .group_by(GrantCall.bdns_code)
                    .having(func.count() > 1)
                    .subquery()
                )
            ) or 0
            missing_codes = session.scalar(
                select(func.count()).select_from(GrantCall).where(GrantCall.bdns_code.is_(None))
            ) or 0
            invalid_dates = session.scalar(
                select(func.count()).select_from(GrantCall).where(
                    GrantCall.application_start_date > GrantCall.application_end_date
                )
            ) or 0
            orphan_raw = session.execute(
                text(
                    "select count(*) from core.grant_calls c "
                    "left join raw.bdns_grant_calls r on r.id = c.raw_id "
                    "where r.id is null"
                )
            ).scalar_one()
            orphan_relations = 0
            for table in (
                "grant_call_sectors",
                "grant_call_regions",
                "grant_call_beneficiary_types",
                "grant_call_funds",
                "grant_call_organizations",
            ):
                orphan_relations += session.execute(
                    text(
                        f"select count(*) from core.{table} r "
                        "left join core.grant_calls c on c.id = r.grant_call_id "
                        "where c.id is null"
                    )
                ).scalar_one()
            unresolved_failures = session.scalar(
                select(func.count()).select_from(IngestionFailure).where(IngestionFailure.resolved_at.is_(None))
            ) or 0

        checks = {
            "duplicate CORE BDNS codes": duplicate_core,
            "CORE calls without BDNS code": missing_codes,
            "invalid CORE date ranges": invalid_dates,
            "orphan CORE RAW references": orphan_raw,
            "orphan CORE relation references": orphan_relations,
            "unresolved ingestion failures": unresolved_failures,
        }
        violations.extend(f"{label}={count}" for label, count in checks.items() if count)
        print(f"CORE grant calls: {core_count}")
        if violations:
            print("QUALITY GATE FAILED")
            for violation in violations:
                print(f"- {violation}")
            return 1
        print("QUALITY GATE PASSED")
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
