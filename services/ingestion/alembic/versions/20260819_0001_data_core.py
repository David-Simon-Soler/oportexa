"""create RAW and CORE data core schemas

Revision ID: 20260819_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260819_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA raw")
    op.execute("CREATE SCHEMA core")

    op.create_table(
        "bdns_grant_calls",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("bdns_code", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("source_endpoint", sa.Text(), nullable=False),
        sa.Column("source_retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("bdns_code", name="uq_raw_bdns_grant_calls_bdns_code"),
        schema="raw",
    )
    op.create_index("ix_raw_bdns_grant_calls_bdns_code", "bdns_grant_calls", ["bdns_code"], schema="raw")
    op.create_index("ix_raw_bdns_grant_calls_payload_hash", "bdns_grant_calls", ["payload_hash"], schema="raw")

    op.create_table(
        "organizations",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source_key", sa.String(512), nullable=False),
        sa.Column("level1", sa.Text()), sa.Column("level2", sa.Text()), sa.Column("level3", sa.Text()),
        sa.UniqueConstraint("source_key", name="uq_core_organizations_source_key"), schema="core",
    )
    op.create_table(
        "sectors",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source_key", sa.String(512), nullable=False), sa.Column("code", sa.String(64)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("source_key", name="uq_core_sectors_source_key"), schema="core",
    )
    op.create_index("ix_core_sectors_code", "sectors", ["code"], schema="core")
    op.create_table(
        "regions",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source_key", sa.String(512), nullable=False), sa.Column("code", sa.String(64)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("source_key", name="uq_core_regions_source_key"), schema="core",
    )
    op.create_index("ix_core_regions_code", "regions", ["code"], schema="core")
    op.create_table(
        "beneficiary_types",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source_key", sa.String(512), nullable=False), sa.Column("code", sa.String(64)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("source_key", name="uq_core_beneficiary_types_source_key"), schema="core",
    )
    op.create_index("ix_core_beneficiary_types_code", "beneficiary_types", ["code"], schema="core")
    op.create_table(
        "funds",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source_key", sa.String(512), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("source_key", name="uq_core_funds_source_key"), schema="core",
    )
    op.create_table(
        "grant_calls",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("bdns_code", sa.String(64), nullable=False),
        sa.Column("raw_id", sa.BigInteger(), sa.ForeignKey("raw.bdns_grant_calls.id"), nullable=False),
        sa.Column("title", sa.Text()), sa.Column("description", sa.Text()), sa.Column("call_type", sa.Text()),
        sa.Column("total_budget", sa.Numeric(20, 2)), sa.Column("is_open", sa.Boolean()),
        sa.Column("application_start_date", sa.Date()), sa.Column("application_end_date", sa.Date()),
        sa.Column("purpose_description", sa.Text()), sa.Column("regulatory_bases_description", sa.Text()),
        sa.Column("regulatory_bases_url", sa.Text()), sa.Column("electronic_office_url", sa.Text()),
        sa.Column("source_received_date", sa.Date()), sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("bdns_code", name="uq_core_grant_calls_bdns_code"), schema="core",
    )
    op.create_index("ix_core_grant_calls_bdns_code", "grant_calls", ["bdns_code"], schema="core")
    op.create_index("ix_core_grant_calls_application_dates", "grant_calls", ["application_start_date", "application_end_date"], schema="core")
    op.create_index("ix_core_grant_calls_is_open", "grant_calls", ["is_open"], schema="core")
    op.create_index("ix_core_grant_calls_source_received_date", "grant_calls", ["source_received_date"], schema="core")

    associations = {
        "grant_call_organizations": ("organization_id", "organizations"),
        "grant_call_sectors": ("sector_id", "sectors"),
        "grant_call_regions": ("region_id", "regions"),
        "grant_call_beneficiary_types": ("beneficiary_type_id", "beneficiary_types"),
        "grant_call_funds": ("fund_id", "funds"),
    }
    for table_name, (column_name, target_table) in associations.items():
        op.create_table(
            table_name,
            sa.Column("grant_call_id", sa.BigInteger(), sa.ForeignKey("core.grant_calls.id", ondelete="CASCADE"), primary_key=True),
            sa.Column(column_name, sa.BigInteger(), sa.ForeignKey(f"core.{target_table}.id", ondelete="CASCADE"), primary_key=True),
            schema="core",
        )


def downgrade() -> None:
    op.execute("DROP SCHEMA core CASCADE")
    op.execute("DROP SCHEMA raw CASCADE")

