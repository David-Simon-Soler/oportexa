import json

import httpx
import pytest

from opportunity_ingestion.bdns.client import BdnsClient
from opportunity_ingestion.bdns.config import BdnsConfig
from opportunity_ingestion.bdns.exceptions import BdnsHttpError, BdnsInvalidJsonError, BdnsRequestError


def client_for(handler, **kwargs):
    transport = httpx.MockTransport(handler)
    config = BdnsConfig(pause_seconds=0, max_retries=0, **kwargs)
    return BdnsClient(config, transport=transport)


def test_search_builds_confirmed_request():
    def handler(request):
        assert request.url.path == "/bdnstrans/api/convocatorias/busqueda"
        assert request.url.params["page"] == "0"
        assert request.url.params["pageSize"] == "2"
        assert request.url.params["fechaDesde"] == "2026-08-18"
        return httpx.Response(200, json={"content": [{"numeroConvocatoria": "1", "descripcion": "Test"}], "last": True})

    with client_for(handler) as client:
        result = client.search_calls(page_size=2, fechaDesde="2026-08-18")
    assert result.content[0].numero_convocatoria == "1"


def test_valid_detail_and_optional_fields():
    payload = {"codigoBDNS": "1", "descripcion": "Test", "documentos": [], "fondos": None}
    with client_for(lambda request: httpx.Response(200, json=payload)) as client:
        result = client.get_call_detail("1")
    assert result.codigo_bdns == "1"
    assert result.descripcion == "Test"
    assert result.documentos == []


def test_unknown_fields_are_tolerated():
    with client_for(lambda request: httpx.Response(200, json={"content": [], "newField": "future"})) as client:
        result = client.search_calls()
    assert result.content == []
    assert result.model_extra["newField"] == "future"


def test_invalid_json_raises():
    with client_for(lambda request: httpx.Response(200, content=b"not-json")) as client:
        with pytest.raises(BdnsInvalidJsonError):
            client.search_calls()


def test_http_errors_are_identified():
    for status in (404, 429, 500):
        with client_for(lambda request, status=status: httpx.Response(status)) as client:
            with pytest.raises(BdnsHttpError) as error:
                client.search_calls()
        assert error.value.status_code == status


def test_timeout_is_identified():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with client_for(handler) as client:
        with pytest.raises(BdnsRequestError):
            client.search_calls()


def test_pagination_stops_at_last_page():
    requests = []

    def handler(request):
        requests.append(request.url.params["page"])
        page = int(request.url.params["page"])
        return httpx.Response(200, json={
            "content": [{"numeroConvocatoria": str(page)}],
            "last": page == 1,
        })

    with client_for(handler) as client:
        pages = list(client.iter_search_calls(max_pages=10))
    assert requests == ["0", "1"]
    assert [page.content[0].numero_convocatoria for page in pages] == ["0", "1"]


def test_pagination_can_resume_from_a_confirmed_page():
    requests = []

    def handler(request):
        requests.append(request.url.params["page"])
        page = int(request.url.params["page"])
        return httpx.Response(200, json={"content": [{"numeroConvocatoria": str(page)}], "last": page == 2})

    with client_for(handler) as client:
        pages = list(client.iter_search_calls(start_page=2, max_pages=2))
    assert requests == ["2"]
    assert pages[0].content[0].numero_convocatoria == "2"


def test_page_size_limit_is_enforced():
    with client_for(lambda request: httpx.Response(200, json={"content": []})) as client:
        with pytest.raises(ValueError):
            client.search_calls(page_size=10_001)
