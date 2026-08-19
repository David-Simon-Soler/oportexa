#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select, text

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.db.models import (  # noqa: E402
    BeneficiaryType,
    GrantCall,
    GrantCallBeneficiaryType,
    GrantCallOrganization,
    GrantCallRegion,
    GrantCallSector,
    Organization,
    RawBdnsGrantCall,
    Region,
    Sector,
)
from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402


def percentage(count: int, total: int) -> str:
    return "0.00%" if total == 0 else f"{count / total * 100:.2f}%"


def main() -> int:
    engine = create_db_engine()
    try:
        with session_factory(engine)() as session:
            total = session.scalar(select(func.count()).select_from(GrantCall)) or 0
            raw_total = session.scalar(select(func.count()).select_from(RawBdnsGrantCall)) or 0
            raw_unique_codes = session.scalar(select(func.count(func.distinct(RawBdnsGrantCall.bdns_code)))) or 0
            unique_codes = session.scalar(select(func.count(func.distinct(GrantCall.bdns_code)))) or 0
            print(f"CORE grant calls: {total}")
            print(f"RAW grant calls: {raw_total}")
            print(f"Unique RAW BDNS codes: {raw_unique_codes}")
            print(f"Unique CORE BDNS codes: {unique_codes}")
            print(f"Duplicate RAW BDNS codes: {raw_total - raw_unique_codes}")
            print(f"Duplicate CORE BDNS codes: {total - unique_codes}")
            for label, condition in (
                ("without budget", GrantCall.total_budget.is_(None)),
                ("without start date", GrantCall.application_start_date.is_(None)),
                ("without end date", GrantCall.application_end_date.is_(None)),
                ("without organization", ~GrantCall.id.in_(select(GrantCallOrganization.grant_call_id))),
                ("without regions", ~GrantCall.id.in_(select(GrantCallRegion.grant_call_id))),
                ("without sectors", ~GrantCall.id.in_(select(GrantCallSector.grant_call_id))),
                ("without beneficiaries", ~GrantCall.id.in_(select(GrantCallBeneficiaryType.grant_call_id))),
            ):
                count = session.scalar(select(func.count()).select_from(GrantCall).where(condition)) or 0
                print(f"{label}: {count} ({percentage(count, total)})")
            multi_regions = session.scalar(select(func.count()).select_from(select(GrantCallRegion.grant_call_id).group_by(GrantCallRegion.grant_call_id).having(func.count() > 1).subquery())) or 0
            multi_sectors = session.scalar(select(func.count()).select_from(select(GrantCallSector.grant_call_id).group_by(GrantCallSector.grant_call_id).having(func.count() > 1).subquery())) or 0
            print(f"with multiple regions: {multi_regions}")
            print(f"with multiple sectors: {multi_sectors}")
            orphan_raw = session.execute(text("select count(*) from core.grant_calls c left join raw.bdns_grant_calls r on r.id = c.raw_id where r.id is null")).scalar_one()
            orphan_relations = 0
            for table in ("grant_call_sectors", "grant_call_regions", "grant_call_beneficiary_types", "grant_call_funds", "grant_call_organizations"):
                orphan_relations += session.execute(text(f"select count(*) from core.{table} r left join core.grant_calls c on c.id = r.grant_call_id where c.id is null")).scalar_one()
            print(f"orphan CORE raw references: {orphan_raw}")
            print(f"orphan relation references: {orphan_relations}")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
