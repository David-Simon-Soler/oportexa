from __future__ import annotations

import logging
import time
from collections.abc import Iterator, Mapping
from typing import Any

import httpx

from .config import BdnsConfig
from .exceptions import BdnsHttpError, BdnsInvalidJsonError, BdnsRequestError
from .models import RawCallDetail, RawPage

logger = logging.getLogger(__name__)


class BdnsClient:
    """Small, read-only client for the confirmed public SNPSAP endpoints."""

    def __init__(self, config: BdnsConfig | None = None, *, transport: httpx.BaseTransport | None = None) -> None:
        self.config = config or BdnsConfig.from_env()
        self._last_request_at: float | None = None
        self._http = httpx.Client(
            base_url=self.config.base_url,
            timeout=httpx.Timeout(self.config.timeout_seconds),
            headers={"Accept": "application/json", "User-Agent": self.config.user_agent},
            transport=transport,
        )

    def __enter__(self) -> "BdnsClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def _wait_before_request(self) -> None:
        if self._last_request_at is None:
            return
        remaining = self.config.pause_seconds - (time.monotonic() - self._last_request_at)
        if remaining > 0:
            time.sleep(remaining)

    def _get_json(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        attempts = 0
        while True:
            self._wait_before_request()
            started = time.perf_counter()
            try:
                response = self._http.get(path, params=params)
                self._last_request_at = time.monotonic()
            except httpx.TimeoutException as exc:
                self._last_request_at = time.monotonic()
                if attempts < self.config.max_retries:
                    attempts += 1
                    time.sleep(2**(attempts - 1))
                    continue
                raise BdnsRequestError("BDNS request timed out") from exc
            except httpx.RequestError as exc:
                self._last_request_at = time.monotonic()
                if attempts < self.config.max_retries:
                    attempts += 1
                    time.sleep(2**(attempts - 1))
                    continue
                raise BdnsRequestError("BDNS request failed") from exc

            duration_ms = (time.perf_counter() - started) * 1000
            logger.info("BDNS request completed endpoint=%s status=%s duration_ms=%.0f", path, response.status_code, duration_ms)
            if response.status_code == 429 or response.status_code >= 500:
                if attempts < self.config.max_retries:
                    attempts += 1
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else 2 ** (attempts - 1)
                    time.sleep(delay)
                    continue
            if response.is_error:
                raise BdnsHttpError(response.status_code, str(response.url))
            try:
                return response.json()
            except ValueError as exc:
                raise BdnsInvalidJsonError(f"Invalid JSON from {response.url}") from exc

    def search_calls(self, *, page: int = 0, page_size: int | None = None, **filters: Any) -> RawPage:
        size = page_size or self.config.page_size
        if not 1 <= size <= 10_000:
            raise ValueError("page_size must be between 1 and 10000")
        params = {"page": page, "pageSize": size, **{key: value for key, value in filters.items() if value is not None}}
        return RawPage.model_validate(self._get_json("/convocatorias/busqueda", params))

    def latest_calls(self, *, page: int = 0, page_size: int | None = None) -> RawPage:
        size = page_size or self.config.page_size
        if not 1 <= size <= 10_000:
            raise ValueError("page_size must be between 1 and 10000")
        return RawPage.model_validate(self._get_json("/convocatorias/ultimas", {"page": page, "pageSize": size}))

    def iter_search_calls(self, *, max_pages: int | None = None, page_size: int | None = None, **filters: Any) -> Iterator[RawPage]:
        page = 0
        while max_pages is None or page < max_pages:
            result = self.search_calls(page=page, page_size=page_size, **filters)
            yield result
            if result.last is True or not result.content:
                break
            page += 1

    def get_call_detail(self, bdns_code: str, *, portal_id: str | None = None) -> RawCallDetail:
        if not bdns_code.strip():
            raise ValueError("bdns_code must not be empty")
        params: dict[str, Any] = {"numConv": bdns_code}
        if portal_id is not None:
            params["vpd"] = portal_id
        return RawCallDetail.model_validate(self._get_json("/convocatorias", params))

