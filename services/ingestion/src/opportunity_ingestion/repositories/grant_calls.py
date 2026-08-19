from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from opportunity_ingestion.db.models import (
    BeneficiaryType,
    Fund,
    GrantCall,
    GrantCallBeneficiaryType,
    GrantCallFund,
    GrantCallOrganization,
    GrantCallRegion,
    GrantCallSector,
    Organization,
    Region,
    Sector,
)
from opportunity_ingestion.transformers.grant_call import CatalogValue, CoreGrantCallData, OrganizationValue


def _upsert_catalog(session: Session, model: type, value: CatalogValue):
    row = session.scalar(select(model).where(model.source_key == value.source_key))
    if row is None:
        attributes = {"source_key": value.source_key, "description": value.description}
        if hasattr(model, "code"):
            attributes["code"] = value.code
        row = model(**attributes)
        session.add(row)
        session.flush()
    return row


def _upsert_organization(session: Session, value: OrganizationValue) -> Organization:
    row = session.scalar(select(Organization).where(Organization.source_key == value.source_key))
    if row is None:
        row = Organization(source_key=value.source_key, level1=value.level1, level2=value.level2, level3=value.level3)
        session.add(row)
        session.flush()
    return row


def _sync_relation(session: Session, model: type, grant_call_id: int, foreign_key: str, desired_ids: set[int]) -> None:
    rows = session.scalars(select(model).where(model.grant_call_id == grant_call_id)).all()
    current_ids = {getattr(row, foreign_key) for row in rows}
    for row in rows:
        if getattr(row, foreign_key) not in desired_ids:
            session.delete(row)
    for item_id in desired_ids - current_ids:
        session.add(model(grant_call_id=grant_call_id, **{foreign_key: item_id}))


def upsert_core_grant_call(
    session: Session,
    *,
    data: CoreGrantCallData,
    raw_id: int,
    observed_at: datetime | None = None,
) -> tuple[GrantCall, bool]:
    now = observed_at or datetime.now(timezone.utc)
    row = session.scalar(select(GrantCall).where(GrantCall.bdns_code == data.bdns_code))
    is_new = row is None
    if row is None:
        row = GrantCall(bdns_code=data.bdns_code, raw_id=raw_id, first_seen_at=now, last_seen_at=now)
        session.add(row)
    row.raw_id = raw_id
    row.title = data.title
    row.description = data.description
    row.call_type = data.call_type
    row.total_budget = data.total_budget
    row.is_open = data.is_open
    row.application_start_date = data.application_start_date
    row.application_end_date = data.application_end_date
    row.purpose_description = data.purpose_description
    row.regulatory_bases_description = data.regulatory_bases_description
    row.regulatory_bases_url = data.regulatory_bases_url
    row.electronic_office_url = data.electronic_office_url
    row.source_received_date = data.source_received_date
    row.last_seen_at = now
    session.flush()

    organization_ids: set[int] = set()
    if data.organization is not None:
        organization_ids.add(_upsert_organization(session, data.organization).id)
    sector_ids = {_upsert_catalog(session, Sector, value).id for value in data.sectors}
    region_ids = {_upsert_catalog(session, Region, value).id for value in data.regions}
    beneficiary_ids = {_upsert_catalog(session, BeneficiaryType, value).id for value in data.beneficiary_types}
    fund_ids = {_upsert_catalog(session, Fund, value).id for value in data.funds}

    _sync_relation(session, GrantCallOrganization, row.id, "organization_id", organization_ids)
    _sync_relation(session, GrantCallSector, row.id, "sector_id", sector_ids)
    _sync_relation(session, GrantCallRegion, row.id, "region_id", region_ids)
    _sync_relation(session, GrantCallBeneficiaryType, row.id, "beneficiary_type_id", beneficiary_ids)
    _sync_relation(session, GrantCallFund, row.id, "fund_id", fund_ids)
    session.flush()
    return row, is_new


def counts(session: Session) -> dict[str, int]:
    result: dict[str, int] = {}
    raw_model = __import__("opportunity_ingestion.db.models", fromlist=["RawBdnsGrantCall"]).RawBdnsGrantCall
    result["raw_grant_calls"] = session.scalar(select(func.count()).select_from(raw_model)) or 0
    for name, model in {
        "grant_calls": GrantCall,
        "organizations": Organization,
        "sectors": Sector,
        "regions": Region,
        "beneficiary_types": BeneficiaryType,
        "funds": Fund,
    }.items():
        result[name] = session.scalar(select(func.count()).select_from(model)) or 0
    return result
