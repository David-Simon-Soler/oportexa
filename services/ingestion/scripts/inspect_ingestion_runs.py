#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.backfill.ops import unresolved_failure_count  # noqa: E402
from opportunity_ingestion.db.models import IngestionFailure, IngestionRun  # noqa: E402
from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only inspection of BDNS backfill runs and unresolved failures.")
    parser.add_argument("--failed", action="store_true", help="Show unresolved failures instead of only run summaries.")
    args = parser.parse_args()
    engine = create_db_engine()
    try:
        with session_factory(engine)() as session:
            runs = session.scalars(select(IngestionRun).order_by(IngestionRun.id)).all()
            print("Runs:")
            for run in runs:
                print(f"run={run.id} window={run.date_from}..{run.date_to} status={run.status} fetched={run.fetched} succeeded={run.succeeded} failed={run.failed} last_page={run.last_page} started_at={run.started_at} completed_at={run.completed_at}")
            failures = session.scalars(
                select(IngestionFailure)
                .where(IngestionFailure.resolved_at.is_(None))
                .order_by(IngestionFailure.id)
            ).all()
            print(f"Unresolved failures: {unresolved_failure_count(session)}")
            if args.failed:
                for failure in failures:
                    print(f"failure={failure.id} run={failure.ingestion_run_id} bdns_code={failure.bdns_code} stage={failure.stage} type={failure.error_type} attempts={failure.attempts} last_attempt_at={failure.last_attempt_at} message={failure.error_message}")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
