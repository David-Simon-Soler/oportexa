#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.db.session import create_db_engine, session_factory  # noqa: E402
from opportunity_ingestion.repositories.grant_calls import counts  # noqa: E402


def main() -> int:
    engine = create_db_engine()
    try:
        with session_factory(engine)() as session:
            for name, value in counts(session).items():
                print(f"{name.replace('_', ' ').title()}: {value}")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

