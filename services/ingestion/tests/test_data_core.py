from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from opportunity_ingestion.bdns.models import RawCallDetail, RawNestedDescription, RawOrgan
from opportunity_ingestion.etl import ingest_calls
from opportunity_ingestion.repositories.raw_grant_calls import canonical_payload_hash
from opportunity_ingestion.transformers.grant_call import raw_payload, transform_call


def detail(**overrides):
    values = {
        "codigoBDNS": "925673",
        "organo": {"nivel1": "LOCAL", "nivel2": "MORELL, EL", "nivel3": "AYUNTAMIENTO DE EL MORELL"},
        "descripcion": "Ayudas de prueba",
        "tipoConvocatoria": "Concesión directa - canónica",
        "presupuestoTotal": 10000,
        "abierto": False,
        "fechaRecepcion": "2026-08-19",
        "fechaInicioSolicitud": "2026-08-24",
        "fechaFinSolicitud": "2026-10-06",
        "sectores": [{"codigo": "Q", "descripcion": "EDUCACIÓN"}],
        "regiones": [{"descripcion": "ES514 - Tarragona"}],
        "tiposBeneficiarios": [{"descripcion": "PERSONAS FÍSICAS"}],
        "fondos": [],
    }
    values.update(overrides)
    return RawCallDetail.model_validate(values)


def test_hash_is_stable_and_changes_with_payload():
    first = {"b": 2, "a": ["á"]}
    same = {"a": ["á"], "b": 2}
    changed = {"a": ["á"], "b": 3}
    assert canonical_payload_hash(first) == canonical_payload_hash(same)
    assert canonical_payload_hash(first) != canonical_payload_hash(changed)


def test_transformer_preserves_verified_fields_and_decimal():
    result = transform_call(detail())
    assert result.bdns_code == "925673"
    assert result.total_budget == Decimal("10000")
    assert result.application_start_date == date(2026, 8, 24)
    assert result.sectors[0].code == "Q"
    assert result.regions[0].code == "ES514"
    assert result.organization.level3 == "AYUNTAMIENTO DE EL MORELL"


def test_transformer_handles_nulls_and_empty_arrays():
    result = transform_call(detail(organo=None, sectores=None, regiones=[], tiposBeneficiarios=None, fondos=None, presupuestoTotal=None))
    assert result.organization is None
    assert result.sectors == ()
    assert result.regions == ()
    assert result.beneficiary_types == ()
    assert result.funds == ()
    assert result.total_budget is None


def test_raw_payload_uses_official_aliases_without_inventing_fields():
    payload = raw_payload(detail())
    assert payload["codigoBDNS"] == "925673"
    assert "bdns_code" not in payload


class FakeClient:
    def __init__(self, items, details):
        self.config = SimpleNamespace(page_size=5, base_url="https://example.invalid/api")
        self.items = items
        self.details = details

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def iter_search_calls(self, **kwargs):
        yield SimpleNamespace(content=self.items)

    def get_call_detail(self, code):
        value = self.details[code]
        if isinstance(value, Exception):
            raise value
        return value


def test_dry_run_does_not_create_database_and_continues_after_item_error(monkeypatch):
    good = detail()
    bad = RuntimeError("synthetic detail failure")
    fake = FakeClient([SimpleNamespace(numero_convocatoria="925673"), SimpleNamespace(numero_convocatoria="broken")], {"925673": good, "broken": bad})
    monkeypatch.setattr("opportunity_ingestion.etl.BdnsClient", lambda: fake)
    monkeypatch.setattr("opportunity_ingestion.etl.create_db_engine", lambda: pytest.fail("database must not be created in dry-run"))

    result = ingest_calls(date_from=date(2026, 8, 18), date_to=date(2026, 8, 19), limit=2, dry_run=True)
    assert result.fetched == 1
    assert result.new == 1
    assert result.failed == 1
