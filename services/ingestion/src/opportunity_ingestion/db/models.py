from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, JSON, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    __table_args__ = {"schema": "ops"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched: Mapped[int] = mapped_column(default=0, nullable=False)
    succeeded: Mapped[int] = mapped_column(default=0, nullable=False)
    failed: Mapped[int] = mapped_column(default=0, nullable=False)
    last_page: Mapped[int | None] = mapped_column()
    error_summary: Mapped[str | None] = mapped_column(Text)


class IngestionFailure(Base):
    __tablename__ = "ingestion_failures"
    __table_args__ = {"schema": "ops"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ops.ingestion_runs.id", ondelete="CASCADE"), nullable=False)
    bdns_code: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    error_type: Mapped[str] = mapped_column(String(128), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(default=1, nullable=False)
    first_failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RawBdnsGrantCall(Base):
    __tablename__ = "bdns_grant_calls"
    __table_args__ = {"schema": "raw"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bdns_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    source_retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    level1: Mapped[str | None] = mapped_column(Text)
    level2: Mapped[str | None] = mapped_column(Text)
    level3: Mapped[str | None] = mapped_column(Text)


class Sector(Base):
    __tablename__ = "sectors"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Region(Base):
    __tablename__ = "regions"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class BeneficiaryType(Base):
    __tablename__ = "beneficiary_types"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Fund(Base):
    __tablename__ = "funds"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class GrantCall(Base):
    __tablename__ = "grant_calls"
    __table_args__ = (
        UniqueConstraint("bdns_code", name="uq_grant_calls_bdns_code"),
        Index("ix_grant_calls_application_dates", "application_start_date", "application_end_date"),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bdns_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_id: Mapped[int] = mapped_column(ForeignKey("raw.bdns_grant_calls.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    call_type: Mapped[str | None] = mapped_column(Text)
    total_budget: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    is_open: Mapped[bool | None] = mapped_column(Boolean, index=True)
    application_start_date: Mapped[date | None] = mapped_column(Date)
    application_end_date: Mapped[date | None] = mapped_column(Date)
    purpose_description: Mapped[str | None] = mapped_column(Text)
    regulatory_bases_description: Mapped[str | None] = mapped_column(Text)
    regulatory_bases_url: Mapped[str | None] = mapped_column(Text)
    electronic_office_url: Mapped[str | None] = mapped_column(Text)
    source_received_date: Mapped[date | None] = mapped_column(Date, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class GrantCallOrganization(Base):
    __tablename__ = "grant_call_organizations"
    __table_args__ = {"schema": "core"}
    grant_call_id: Mapped[int] = mapped_column(ForeignKey("core.grant_calls.id", ondelete="CASCADE"), primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("core.organizations.id", ondelete="CASCADE"), primary_key=True)


class GrantCallSector(Base):
    __tablename__ = "grant_call_sectors"
    __table_args__ = {"schema": "core"}
    grant_call_id: Mapped[int] = mapped_column(ForeignKey("core.grant_calls.id", ondelete="CASCADE"), primary_key=True)
    sector_id: Mapped[int] = mapped_column(ForeignKey("core.sectors.id", ondelete="CASCADE"), primary_key=True)


class GrantCallRegion(Base):
    __tablename__ = "grant_call_regions"
    __table_args__ = {"schema": "core"}
    grant_call_id: Mapped[int] = mapped_column(ForeignKey("core.grant_calls.id", ondelete="CASCADE"), primary_key=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("core.regions.id", ondelete="CASCADE"), primary_key=True)


class GrantCallBeneficiaryType(Base):
    __tablename__ = "grant_call_beneficiary_types"
    __table_args__ = {"schema": "core"}
    grant_call_id: Mapped[int] = mapped_column(ForeignKey("core.grant_calls.id", ondelete="CASCADE"), primary_key=True)
    beneficiary_type_id: Mapped[int] = mapped_column(ForeignKey("core.beneficiary_types.id", ondelete="CASCADE"), primary_key=True)


class GrantCallFund(Base):
    __tablename__ = "grant_call_funds"
    __table_args__ = {"schema": "core"}
    grant_call_id: Mapped[int] = mapped_column(ForeignKey("core.grant_calls.id", ondelete="CASCADE"), primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("core.funds.id", ondelete="CASCADE"), primary_key=True)
