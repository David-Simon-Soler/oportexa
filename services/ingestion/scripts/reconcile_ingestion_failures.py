#!/usr/bin/env python3
"""Reconcile durable ingestion failures against successfully stored CORE calls."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.backfill.ops import (  # noqa: E402
    reconcilable_failure_count,
    reconcile_failures_with_successful_ingestion,
)
from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Persist resolved_at; without it, only preview changes.")
    args = parser.parse_args()
    engine = create_db_engine()
    try:
        with session_factory(engine)() as session:
            candidates = reconcilable_failure_count(session)
            print(f"Pending failures with later successful RAW/CORE evidence: {candidates}")
            if args.apply:
                session.rollback()
                with session.begin():
                    resolved = reconcile_failures_with_successful_ingestion(session)
                print(f"Resolved rows (history retained): {resolved}")
            else:
                print("Dry run: no rows changed. Re-run with --apply to set resolved_at.")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
