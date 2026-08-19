"""add durable ingestion run checkpoints

Revision ID: 20260819_0002
Revises: 20260819_0001
"""

from alembic import op
import sqlalchemy as sa

revision = "20260819_0002"
down_revision = "20260819_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ops")
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("fetched", sa.Integer(), server_default="0", nullable=False),
        sa.Column("succeeded", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_page", sa.Integer()),
        sa.Column("error_summary", sa.Text()),
        sa.CheckConstraint("date_to >= date_from", name="ck_ingestion_runs_date_order"),
        sa.CheckConstraint("fetched >= 0 AND succeeded >= 0 AND failed >= 0", name="ck_ingestion_runs_nonnegative_counts"),
        schema="ops",
    )
    op.create_index("ix_ops_ingestion_runs_source_status", "ingestion_runs", ["source", "status"], schema="ops")
    op.create_index("ix_ops_ingestion_runs_date_window", "ingestion_runs", ["date_from", "date_to"], schema="ops")


def downgrade() -> None:
    op.drop_index("ix_ops_ingestion_runs_date_window", table_name="ingestion_runs", schema="ops")
    op.drop_index("ix_ops_ingestion_runs_source_status", table_name="ingestion_runs", schema="ops")
    op.drop_table("ingestion_runs", schema="ops")
    op.execute("DROP SCHEMA IF EXISTS ops")
