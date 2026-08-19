#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.backfill.runner import BackfillInterrupted, DEFAULT_PAGE_SIZE, run_backfill  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a controlled, resumable BDNS backfill by deterministic date windows.")
    parser.add_argument("--date-from", required=True, type=date.fromisoformat, help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--date-to", required=True, type=date.fromisoformat, help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument("--window", required=True, choices=("daily", "weekly", "monthly"), help="Window partitioning strategy.")
    parser.add_argument("--resume", action="store_true", help="Resume the latest non-completed run for each window and skip completed windows.")
    parser.add_argument("--max-windows", type=int, help="Process at most N windows; useful for controlled tests.")
    parser.add_argument("--limit-per-window", type=int, help="Stop after N successfully fetched details and leave the window interrupted.")
    parser.add_argument("--retry-failed", action="store_true", help="Retry unresolved per-code failures for each resumed run.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without writing runs, failures, RAW or CORE.")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help=f"BDNS listing page size (default: {DEFAULT_PAGE_SIZE}, maximum: 500).")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    try:
        result = run_backfill(
            date_from=args.date_from,
            date_to=args.date_to,
            window=args.window,
            resume=args.resume,
            max_windows=args.max_windows,
            limit_per_window=args.limit_per_window,
            retry_failed=args.retry_failed,
            dry_run=args.dry_run,
            page_size=args.page_size,
        )
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))
    except (KeyboardInterrupt, BackfillInterrupted) as error:
        logging.getLogger(__name__).warning("Backfill interrupted: %s", error)
        return 130
    print("Backfill completed")
    print(f"Windows: {result.windows}")
    print(f"Skipped: {result.skipped}")
    print(f"Pages: {result.pages}")
    print(f"Fetched: {result.fetched}")
    print(f"Succeeded: {result.succeeded}")
    print(f"Failed: {result.failed}")
    print(f"New: {result.new}")
    print(f"Updated: {result.updated}")
    print(f"Unchanged: {result.unchanged}")
    print(f"Requests approximately: {result.requests_approx}")
    print(f"Duration seconds: {result.duration_seconds:.3f}")
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
