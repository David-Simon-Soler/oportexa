#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.etl import ingest_calls  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a small BDNS call window into PostgreSQL.")
    parser.add_argument("--date-from", required=True, type=date.fromisoformat)
    parser.add_argument("--date-to", required=True, type=date.fromisoformat)
    parser.add_argument("--limit", required=True, type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    summary = ingest_calls(date_from=args.date_from, date_to=args.date_to, limit=args.limit, dry_run=args.dry_run)
    print("Ingestion completed")
    print(f"Fetched: {summary.fetched}")
    print(f"New: {summary.new}")
    print(f"Updated: {summary.updated}")
    print(f"Unchanged: {summary.unchanged}")
    print(f"Failed: {summary.failed}")
    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
