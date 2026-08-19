from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import func, select, text

from opportunity_ingestion.db.models import (
    GrantCall,
    GrantCallSector,
    RawBdnsGrantCall,
    Sector,
)
from opportunity_ingestion.db.session import create_db_engine, session_factory
from opportunity_ingestion.repositories.grant_calls import upsert_core_grant_call
from opportunity_ingestion.repositories.raw_grant_calls import canonical_payload_hash, upsert_raw_grant_call
from opportunity_ingestion.transformers.grant_call import raw_payload, transform_call
from ..test_data_core import detail


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is required for PostgreSQL integration tests")


@pytest.fixture(scope="module")
def test_engine():
    assert TEST_DATABASE_URL
    previous = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    command.upgrade(config, "head")
    engine = create_db_engine(TEST_DATABASE_URL)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE core.grant_call_organizations, core.grant_call_sectors, core.grant_call_regions, core.grant_call_beneficiary_types, core.grant_call_funds, core.grant_calls, core.organizations, core.sectors, core.regions, core.beneficiary_types, core.funds, raw.bdns_grant_calls RESTART IDENTITY CASCADE"))
    yield engine
    engine.dispose()
    if previous is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous


def test_postgres_upsert_and_idempotence(test_engine):
    now = datetime.now(timezone.utc)
    detail_model = detail()
    payload = raw_payload(detail_model)
    transformed = transform_call(detail_model)
    with session_factory(test_engine)() as session:
        with session.begin():
            raw, changed = upsert_raw_grant_call(session, bdns_code="925673", payload=payload, source_endpoint="test", observed_at=now)
            _, is_new = upsert_core_grant_call(session, data=transformed, raw_id=raw.id, observed_at=now)
        first_hash = raw.payload_hash
        first_raw_id = raw.id
        assert changed is True
        assert is_new is True

        with session.begin():
            raw_again, changed_again = upsert_raw_grant_call(session, bdns_code="925673", payload=payload, source_endpoint="test", observed_at=datetime.now(timezone.utc))
            _, is_new_again = upsert_core_grant_call(session, data=transformed, raw_id=raw_again.id, observed_at=datetime.now(timezone.utc))
        assert changed_again is False
        assert is_new_again is False
        assert raw_again.id == first_raw_id
        assert raw_again.payload_hash == first_hash
        assert session.scalar(select(func.count()).select_from(RawBdnsGrantCall).where(RawBdnsGrantCall.bdns_code == "925673")) == 1
        assert session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.bdns_code == "925673")) == 1
        assert session.scalar(select(func.count()).select_from(GrantCallSector)) == 1


def test_postgres_payload_change_updates_raw_and_core(test_engine):
    changed_detail = detail(descripcion="Ayudas de prueba corregidas", presupuestoTotal=12000)
    with session_factory(test_engine)() as session:
        with session.begin():
            raw, changed = upsert_raw_grant_call(session, bdns_code="925673", payload=raw_payload(changed_detail), source_endpoint="test", observed_at=datetime.now(timezone.utc))
            _, is_new = upsert_core_grant_call(session, data=transform_call(changed_detail), raw_id=raw.id)
        assert changed is True
        assert is_new is False
        stored = session.scalar(select(GrantCall).where(GrantCall.bdns_code == "925673"))
        assert stored.description == "Ayudas de prueba corregidas"
        assert stored.total_budget == 12000
        assert raw.payload_hash == canonical_payload_hash(raw_payload(changed_detail))


def test_postgres_transaction_rolls_back_raw_and_core_together(test_engine):
    with pytest.raises(RuntimeError):
        with session_factory(test_engine)() as session:
            with session.begin():
                raw, _ = upsert_raw_grant_call(session, bdns_code="transaction-test", payload=raw_payload(detail()), source_endpoint="test")
                upsert_core_grant_call(session, data=transform_call(detail()), raw_id=raw.id)
                raise RuntimeError("synthetic failure after both layers")
    with session_factory(test_engine)() as session:
        assert session.scalar(select(func.count()).select_from(RawBdnsGrantCall).where(RawBdnsGrantCall.bdns_code == "transaction-test")) == 0
        assert session.scalar(select(func.count()).select_from(GrantCall).where(GrantCall.bdns_code == "transaction-test")) == 0
