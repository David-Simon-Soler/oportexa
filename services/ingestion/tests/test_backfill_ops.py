from __future__ import annotations

from datetime import date

from opportunity_ingestion.backfill import runner
from opportunity_ingestion.backfill.ops import database_error_details, release_window_lock


class _LockConnection:
    def __init__(self) -> None:
        self.execution_options_seen: dict[str, str] | None = None
        self.statements: list[str] = []

    def execution_options(self, **options):
        self.execution_options_seen = options
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, _parameters):
        self.statements.append(str(statement))
        return type("Result", (), {"scalar_one": lambda _self: True})()


class _Engine:
    def __init__(self) -> None:
        self.connection = _LockConnection()
        self.disposed = False

    def connect(self):
        return self.connection

    def dispose(self):
        self.disposed = True


def test_backfill_lock_connection_uses_autocommit(monkeypatch):
    engine = _Engine()
    monkeypatch.setattr(runner, "create_db_engine", lambda: engine)
    monkeypatch.setattr(runner, "_run_window", lambda *_args, **_kwargs: None)

    runner.run_backfill(date_from=date(2026, 1, 1), date_to=date(2026, 1, 1), window="daily")

    assert engine.connection.execution_options_seen == {"isolation_level": "AUTOCOMMIT"}
    assert len(engine.connection.statements) == 2
    assert engine.disposed is True


def test_release_invalid_connection_is_controlled(caplog):
    class InvalidConnection:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("connection is closed")

    with caplog.at_level("WARNING"):
        release_window_lock(InvalidConnection(), "test-window")

    assert "window_lock_release_failed" in caplog.text
    assert "connection is closed" in caplog.text


def test_database_error_details_reads_postgresql_diagnostics():
    class Diagnostic:
        sqlstate = "23505"
        constraint_name = "uq_core_grant_calls_bdns_code"
        message_detail = "Key (bdns_code)=(925666) already exists."

    class Original:
        diag = Diagnostic()

    error = type("IntegrityError", (), {"orig": Original()})()

    assert database_error_details(error) == {
        "sqlstate": "23505",
        "constraint": "uq_core_grant_calls_bdns_code",
        "detail": "Key (bdns_code)=(925666) already exists.",
    }
