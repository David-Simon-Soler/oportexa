from datetime import date
import signal

import pytest

from opportunity_ingestion.backfill.runner import BackfillInterrupted, BackfillResult, _consume_record_budget, _install_signal_handler, _restore_signal_handler, run_backfill
from opportunity_ingestion.backfill.windows import generate_windows


def pairs(start, end, kind):
    return [(item.date_from, item.date_to) for item in generate_windows(date.fromisoformat(start), date.fromisoformat(end), kind)]


def test_daily_windows_cover_single_and_partial_ranges():
    assert pairs("2024-01-01", "2024-01-03", "daily") == [(date(2024, 1, 1), date(2024, 1, 1)), (date(2024, 1, 2), date(2024, 1, 2)), (date(2024, 1, 3), date(2024, 1, 3))]
    assert pairs("2024-02-29", "2024-02-29", "daily") == [(date(2024, 2, 29), date(2024, 2, 29))]


def test_weekly_windows_cross_month_without_gaps():
    result = generate_windows(date(2024, 1, 30), date(2024, 2, 12), "weekly")
    assert [(item.date_from, item.date_to) for item in result] == [(date(2024, 1, 30), date(2024, 2, 5)), (date(2024, 2, 6), date(2024, 2, 12))]


@pytest.mark.parametrize(("start", "end", "expected"), [
    ("2024-01-01", "2024-03-31", [("2024-01-01", "2024-01-31"), ("2024-02-01", "2024-02-29"), ("2024-03-01", "2024-03-31")]),
    ("2023-01-15", "2023-03-10", [("2023-01-15", "2023-01-31"), ("2023-02-01", "2023-02-28"), ("2023-03-01", "2023-03-10")]),
    ("2024-04-01", "2024-04-30", [("2024-04-01", "2024-04-30")]),
    ("2024-12-15", "2025-01-10", [("2024-12-15", "2024-12-31"), ("2025-01-01", "2025-01-10")]),
])
def test_monthly_windows_handle_calendar_boundaries(start, end, expected):
    assert [(item.date_from.isoformat(), item.date_to.isoformat()) for item in generate_windows(date.fromisoformat(start), date.fromisoformat(end), "monthly")] == expected


def test_invalid_range_fails_clearly():
    with pytest.raises(ValueError, match="date_from"):
        generate_windows(date(2024, 2, 2), date(2024, 2, 1), "daily")


def test_dry_run_does_not_touch_database(monkeypatch):
    monkeypatch.setattr("opportunity_ingestion.backfill.runner.create_db_engine", lambda: pytest.fail("dry-run must not create a database engine"))
    result = run_backfill(date_from=date(2024, 1, 1), date_to=date(2024, 3, 31), window="monthly", dry_run=True)
    assert result.windows == 3
    assert result.pages == 0


def test_max_records_is_validated_before_database_work(monkeypatch):
    monkeypatch.setattr("opportunity_ingestion.backfill.runner.create_db_engine", lambda: pytest.fail("invalid max_records must not create an engine"))
    with pytest.raises(ValueError, match="max_records"):
        run_backfill(date_from=date(2024, 1, 1), date_to=date(2024, 1, 1), window="daily", max_records=0)


@pytest.mark.parametrize("max_records", [1, 2, 3, 100])
def test_max_records_counts_every_detail_attempt(max_records):
    result = BackfillResult()
    for _ in range(max_records):
        _consume_record_budget(result, max_records)
    assert result.processed == max_records
    with pytest.raises(BackfillInterrupted, match="max_records"):
        _consume_record_budget(result, max_records)


def test_max_records_is_per_execution_and_resume_gets_a_fresh_budget():
    first_execution = BackfillResult(processed=2)
    with pytest.raises(BackfillInterrupted):
        _consume_record_budget(first_execution, 2)
    resumed_execution = BackfillResult()
    _consume_record_budget(resumed_execution, 2)
    assert resumed_execution.processed == 1


def test_sigint_is_deferred_until_safe_checkpoint():
    interrupted_state, previous = _install_signal_handler()
    try:
        signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
        assert interrupted_state["value"] is True
    finally:
        _restore_signal_handler(previous)
