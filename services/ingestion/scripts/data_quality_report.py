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
            print(f"Budget known: {percentage(total - (session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.total_budget.is_(None))) or 0), total)}")
            is_open_known = session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.is_open.is_not(None))) or 0
            is_open_true = session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.is_open.is_(True))) or 0
            print(f"is_open known: {percentage(is_open_known, total)}")
            print(f"is_open true: {percentage(is_open_true, total)}")
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
            average_regions = session.execute(text("""
                select coalesce(avg(item_count), 0)
                from (
                    select c.id, count(r.region_id)::numeric as item_count
                    from core.grant_calls c
                    left join core.grant_call_regions r on r.grant_call_id = c.id
                    group by c.id
                ) counts
            """)).scalar_one()
            average_sectors = session.execute(text("""
                select coalesce(avg(item_count), 0)
                from (
                    select c.id, count(s.sector_id)::numeric as item_count
                    from core.grant_calls c
                    left join core.grant_call_sectors s on s.grant_call_id = c.id
                    group by c.id
                ) counts
            """)).scalar_one()
            print(f"average regions per call: {float(average_regions):.2f}")
            print(f"average sectors per call: {float(average_sectors):.2f}")
            print("Beneficiary type distribution:")
            distribution = session.execute(
                select(BeneficiaryType.description, func.count(func.distinct(GrantCallBeneficiaryType.grant_call_id)))
                .join(GrantCallBeneficiaryType, GrantCallBeneficiaryType.beneficiary_type_id == BeneficiaryType.id)
                .group_by(BeneficiaryType.id, BeneficiaryType.description)
                .order_by(func.count(func.distinct(GrantCallBeneficiaryType.grant_call_id)).desc(), BeneficiaryType.description)
            )
            for description, count in distribution:
                print(f"  {description}: {count} ({percentage(count, total)})")
            orphan_raw = session.execute(text("select count(*) from core.grant_calls c left join raw.bdns_grant_calls r on r.id = c.raw_id where r.id is null")).scalar_one()
            orphan_relations = 0
            for table in ("grant_call_sectors", "grant_call_regions", "grant_call_beneficiary_types", "grant_call_funds", "grant_call_organizations"):
                orphan_relations += session.execute(text(f"select count(*) from core.{table} r left join core.grant_calls c on c.id = r.grant_call_id where c.id is null")).scalar_one()
            print(f"orphan CORE raw references: {orphan_raw}")
            print(f"orphan relation references: {orphan_relations}")
            invalid_dates = session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.application_start_date > GrantCall.application_end_date)) or 0
            missing_codes = session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.bdns_code.is_(None))) or 0
            print(f"invalid date ranges (start after end): {invalid_dates}")
            print(f"missing BDNS codes: {missing_codes}")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
