#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import distinct, func, select

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.db.models import (  # noqa: E402
    BeneficiaryType,
    GrantCall,
    GrantCallBeneficiaryType,
    GrantCallRegion,
    GrantCallSector,
    Region,
    Sector,
)
from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402


def grouped(session, entity, relation, relation_field: str, minimum: int, *, open_only: bool = False) -> None:
    join_field = getattr(relation, relation_field)
    statement = (
        select(entity.description, func.count(distinct(GrantCall.id)).label("count"))
        .join(relation, join_field == entity.id)
        .join(GrantCall, GrantCall.id == relation.grant_call_id)
        .group_by(entity.id, entity.description)
        .having(func.count(distinct(GrantCall.id)) >= minimum)
        .order_by(func.count(distinct(GrantCall.id)).desc(), entity.description)
    )
    if open_only:
        statement = statement.where(GrantCall.is_open.is_(True))
    for description, count in session.execute(statement):
        print(f"{description} | grants={count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only SEO opportunity report over CORE.")
    parser.add_argument("--min-grants", type=int, default=10)
    args = parser.parse_args()
    if args.min_grants < 1:
        parser.error("--min-grants must be positive")
    engine = create_db_engine()
    try:
        with session_factory(engine)() as session:
            print(f"SEO opportunity report | min_grants={args.min_grants}")
            print("WARNING: this report does not create pages or URLs.")
            for title, model, relation, field in (
                ("Top regions", Region, GrantCallRegion, "region_id"),
                ("Top sectors", Sector, GrantCallSector, "sector_id"),
                ("Top beneficiary types", BeneficiaryType, GrantCallBeneficiaryType, "beneficiary_type_id"),
            ):
                print(f"\n## {title}")
                grouped(session, model, relation, field, args.min_grants)
            print("\n## Open grants by region")
            grouped(session, Region, GrantCallRegion, "region_id", args.min_grants, open_only=True)
            print("\n## Open grants by sector")
            grouped(session, Sector, GrantCallSector, "sector_id", args.min_grants, open_only=True)
            print("\n## Region + sector combinations")
            combinations = (
                select(Region.description, Sector.description, func.count(distinct(GrantCall.id)).label("count"))
                .join(GrantCallRegion, GrantCallRegion.region_id == Region.id)
                .join(GrantCall, GrantCall.id == GrantCallRegion.grant_call_id)
                .join(GrantCallSector, GrantCallSector.grant_call_id == GrantCall.id)
                .join(Sector, Sector.id == GrantCallSector.sector_id)
                .group_by(Region.id, Region.description, Sector.id, Sector.description)
                .having(func.count(distinct(GrantCall.id)) >= args.min_grants)
                .order_by(func.count(distinct(GrantCall.id)).desc(), Region.description, Sector.description)
            )
            for region, sector, count in session.execute(combinations):
                print(f"{region} + {sector} | grants={count}")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
