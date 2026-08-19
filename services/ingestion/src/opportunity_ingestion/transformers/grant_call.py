from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import re
from typing import Any

from opportunity_ingestion.bdns.models import RawCallDetail


@dataclass(frozen=True, slots=True)
class CatalogValue:
    source_key: str
    description: str
    code: str | None = None


@dataclass(frozen=True, slots=True)
class OrganizationValue:
    source_key: str
    level1: str | None
    level2: str | None
    level3: str | None


@dataclass(frozen=True, slots=True)
class CoreGrantCallData:
    bdns_code: str
    title: str | None
    description: str | None
    call_type: str | None
    total_budget: Decimal | None
    is_open: bool | None
    application_start_date: date | None
    application_end_date: date | None
    purpose_description: str | None
    regulatory_bases_description: str | None
    regulatory_bases_url: str | None
    electronic_office_url: str | None
    source_received_date: date | None
    organization: OrganizationValue | None
    sectors: tuple[CatalogValue, ...]
    regions: tuple[CatalogValue, ...]
    beneficiary_types: tuple[CatalogValue, ...]
    funds: tuple[CatalogValue, ...]


def _catalog_key(code: str | None, description: str) -> str:
    return f"{code or ''}\x1f{description.strip()}"


def _values(items: list[Any] | None, *, code_allowed: bool = True) -> tuple[CatalogValue, ...]:
    if not items:
        return ()
    result: dict[str, CatalogValue] = {}
    for item in items:
        description = (item.descripcion or "").strip()
        if not description:
            continue
        code = item.codigo if code_allowed else None
        value = CatalogValue(_catalog_key(code, description), description, code)
        result[value.source_key] = value
    return tuple(result.values())


def _regions(items: list[Any] | None) -> tuple[CatalogValue, ...]:
    values: list[CatalogValue] = []
    for item in items or []:
        description = (item.descripcion or "").strip()
        if not description:
            continue
        match = re.match(r"^(\S+)\s+-\s+(.+)$", description)
        code = match.group(1) if match else None
        values.append(CatalogValue(_catalog_key(code, description), description, code))
    return tuple({value.source_key: value for value in values}.values())


def transform_call(detail: RawCallDetail) -> CoreGrantCallData:
    """Map verified raw fields only; no product-level inference is performed."""
    bdns_code = (detail.codigo_bdns or "").strip()
    if not bdns_code:
        raise ValueError("BDNS detail has no codigoBDNS")
    organization = None
    if detail.organo is not None and any((detail.organo.nivel1, detail.organo.nivel2, detail.organo.nivel3)):
        levels = tuple((value or "").strip() for value in (detail.organo.nivel1, detail.organo.nivel2, detail.organo.nivel3))
        organization = OrganizationValue("\x1f".join(levels), *(value or None for value in levels))
    return CoreGrantCallData(
        bdns_code=bdns_code,
        title=detail.descripcion,
        description=detail.descripcion,
        call_type=detail.tipo_convocatoria,
        total_budget=Decimal(str(detail.presupuesto_total)) if detail.presupuesto_total is not None else None,
        is_open=detail.abierto,
        application_start_date=detail.fecha_inicio_solicitud,
        application_end_date=detail.fecha_fin_solicitud,
        purpose_description=detail.descripcion_finalidad,
        regulatory_bases_description=detail.descripcion_bases_reguladoras,
        regulatory_bases_url=detail.url_bases_reguladoras,
        electronic_office_url=detail.sede_electronica,
        source_received_date=detail.fecha_recepcion,
        organization=organization,
        sectors=_values(detail.sectores),
        regions=_regions(detail.regiones),
        beneficiary_types=_values(detail.tipos_beneficiarios),
        funds=_values(detail.fondos, code_allowed=False),
    )


def raw_payload(detail: RawCallDetail) -> dict[str, Any]:
    """Return the provided API fields using their official JSON aliases."""
    return detail.model_dump(by_alias=True, exclude_unset=True, mode="json")

