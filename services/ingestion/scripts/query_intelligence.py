#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, timedelta
from decimal import Decimal
import sys
from pathlib import Path

from sqlalchemy import and_, case, desc, func, or_, select

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.db.models import (  # noqa: E402
    GrantCall,
    GrantCallOrganization,
    GrantCallRegion,
    GrantCallSector,
    Organization,
    Region,
    Sector,
)
from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402


WARNING = "Results reflect only the locally ingested dataset and are not necessarily representative of the full BDNS."


def money(value: Decimal | None) -> str:
    return "unknown" if value is None else f"€{value:,.2f}"


def summary(session) -> None:
    total = session.scalar(select(func.count()).select_from(GrantCall)) or 0
    open_count = session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.is_open.is_(True))) or 0
    known_budget = session.scalar(select(func.sum(GrantCall.total_budget)).where(GrantCall.total_budget.is_not(None)))
    missing_budget = session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.total_budget.is_(None))) or 0
    organizations = session.scalar(select(func.count()).select_from(Organization)) or 0
    regions = session.scalar(select(func.count()).select_from(Region)) or 0
    sectors = session.scalar(select(func.count()).select_from(Sector)) or 0
    print(f"Grant calls: {total}")
    print(f"Open calls: {open_count}")
    print(f"Known total budget: {money(known_budget)}")
    print(f"Calls without budget: {missing_budget}")
    print(f"Organizations: {organizations}")
    print(f"Regions represented: {regions}")
    print(f"Sectors represented: {sectors}")
    print(WARNING)


def grouped(session, model, relation_model, relation_column: str, limit: int) -> None:
    entity = model
    join_column = getattr(relation_model, relation_column)
    statement = (
        select(entity.description, func.count(func.distinct(GrantCall.id)), func.sum(GrantCall.total_budget))
        .join(relation_model, join_column == entity.id)
        .join(GrantCall, GrantCall.id == relation_model.grant_call_id)
        .group_by(entity.id, entity.description)
        .order_by(desc(func.count(func.distinct(GrantCall.id))), entity.description)
        .limit(limit)
    )
    for description, call_count, budget in session.execute(statement):
        print(f"{description} | calls={call_count} | known_budget={money(budget)}")
    print(WARNING)


def closing_soon(session, days: int) -> None:
    today = date.today()
    end = today + timedelta(days=days)
    statement = select(GrantCall).where(
        GrantCall.is_open.is_(True),
        GrantCall.application_end_date.is_not(None),
        GrantCall.application_end_date.between(today, end),
    ).order_by(GrantCall.application_end_date, GrantCall.bdns_code)
    for call in session.scalars(statement):
        print(f"{call.bdns_code} | {call.title or '[no title]'} | end={call.application_end_date} | days_remaining={(call.application_end_date - today).days}")
    print(WARNING)


def search(session, region: str | None, sector: str | None, is_open: bool) -> None:
    statement = select(GrantCall).distinct()
    if region:
        statement = statement.join(GrantCallRegion).join(Region).where(Region.description.ilike(f"%{region}%"))
    if sector:
        statement = statement.join(GrantCallSector).join(Sector).where(Sector.description.ilike(f"%{sector}%"))
    if is_open:
        statement = statement.where(GrantCall.is_open.is_(True))
    statement = statement.order_by(GrantCall.application_end_date.nulls_last(), GrantCall.bdns_code)
    for call in session.scalars(statement):
        print(f"{call.bdns_code} | {call.title or '[no title]'} | open={call.is_open} | end={call.application_end_date or 'unknown'}")
    print(WARNING)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only intelligence queries over the local CORE dataset.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("summary")
    for name in ("top-sectors", "top-regions", "top-organizations"):
        command = sub.add_parser(name)
        command.add_argument("--limit", type=int, default=10)
    closing = sub.add_parser("closing-soon")
    closing.add_argument("--days", type=int, default=30)
    search_parser = sub.add_parser("search")
    search_parser.add_argument("--region")
    search_parser.add_argument("--sector")
    search_parser.add_argument("--open", action="store_true", dest="is_open")
    args = parser.parse_args()
    engine = create_db_engine()
    try:
        with session_factory(engine)() as session:
            if args.command == "summary":
                summary(session)
            elif args.command == "top-sectors":
                grouped(session, Sector, GrantCallSector, "sector_id", args.limit)
            elif args.command == "top-regions":
                grouped(session, Region, GrantCallRegion, "region_id", args.limit)
            elif args.command == "top-organizations":
                statement = (
                    select(Organization.level3, Organization.level2, Organization.level1, func.count(func.distinct(GrantCall.id)), func.sum(GrantCall.total_budget))
                    .join(GrantCallOrganization, Organization.id == GrantCallOrganization.organization_id)
                    .join(GrantCall, GrantCall.id == GrantCallOrganization.grant_call_id)
                    .group_by(Organization.id, Organization.level1, Organization.level2, Organization.level3)
                    .order_by(desc(func.count(func.distinct(GrantCall.id))))
                    .limit(args.limit)
                )
                for level3, level2, level1, call_count, budget in session.execute(statement):
                    print(f"{level3 or level2 or level1 or '[unknown]'} | calls={call_count} | known_budget={money(budget)}")
                print(WARNING)
            elif args.command == "closing-soon":
                closing_soon(session, args.days)
            else:
                search(session, args.region, args.sector, args.is_open)
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
