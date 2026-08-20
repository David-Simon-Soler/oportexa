#!/usr/bin/env python3
"""Read-only comparison between BDNS listing codes and local CORE."""
from __future__ import annotations

import argparse
from datetime import date
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.bdns import BdnsClient  # noqa: E402
from opportunity_ingestion.db.models import GrantCall  # noqa: E402
from opportunity_ingestion.db.session import create_db_engine  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only BDNS announced/listed versus local CORE coverage report.")
    parser.add_argument("--date-from", required=True, type=date.fromisoformat, help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--date-to", required=True, type=date.fromisoformat, help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument("--page-size", type=int, default=500, help="BDNS listing page size; default 500.")
    args = parser.parse_args()
    if args.date_from > args.date_to:
        parser.error("date-from must not be after date-to")
    if not 1 <= args.page_size <= 500:
        parser.error("page-size must be between 1 and 500")

    listed_codes: set[str] = set()
    announced_total: int | None = None
    pages = 0
    with BdnsClient() as client:
        for page in client.iter_search_calls(
            page_size=args.page_size,
            fechaDesde=args.date_from.strftime("%d/%m/%Y"),
            fechaHasta=args.date_to.strftime("%d/%m/%Y"),
        ):
            pages += 1
            if announced_total is None:
                announced_total = page.total_elements
            listed_codes.update(item.numero_convocatoria for item in page.content)

    engine = create_db_engine()
    try:
        with engine.connect() as connection:
            local_codes: set[str] = set()
            sorted_codes = sorted(listed_codes)
            for offset in range(0, len(sorted_codes), 1000):
                batch = sorted_codes[offset : offset + 1000]
                local_codes.update(connection.execute(select(GrantCall.bdns_code).where(GrantCall.bdns_code.in_(batch))).scalars())
    finally:
        engine.dispose()

    missing = listed_codes - local_codes
    listed_count = len(listed_codes)
    coverage = 0.0 if listed_count == 0 else len(local_codes) / listed_count * 100
    status = "COMPLETE" if listed_count > 0 and not missing else "PARTIAL" if listed_count else "NOT COVERED"
    print(f"range={args.date_from}..{args.date_to}")
    print(f"announced_listed_total={announced_total or 0}")
    print(f"unique_listed_codes={listed_count}")
    print(f"local_core_matching={len(local_codes)}")
    print(f"missing_exact_codes={len(missing)}")
    print(f"coverage_percent={coverage:.2f}")
    print(f"pages={pages}")
    print(f"status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
