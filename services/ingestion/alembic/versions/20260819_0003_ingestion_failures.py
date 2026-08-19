"""add durable per-code ingestion failures

Revision ID: 20260819_0003
Revises: 20260819_0002
"""

from alembic import op
import sqlalchemy as sa

revision = "20260819_0003"
down_revision = "20260819_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_ingestion_runs_status",
        "ingestion_runs",
        "status IN ('pending', 'running', 'completed', 'failed', 'interrupted')",
        schema="ops",
    )
    op.create_table(
        "ingestion_failures",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("ingestion_run_id", sa.BigInteger(), sa.ForeignKey("ops.ingestion_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bdns_code", sa.String(64), nullable=False),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("error_type", sa.String(128), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="1", nullable=False),
        sa.Column("first_failed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("attempts > 0", name="ck_ingestion_failures_attempts_positive"),
        schema="ops",
    )
    op.create_index("ix_ops_ingestion_failures_unresolved", "ingestion_failures", ["last_attempt_at"], schema="ops", postgresql_where=sa.text("resolved_at IS NULL"))
    op.create_index("ix_ops_ingestion_failures_bdns_code", "ingestion_failures", ["bdns_code"], schema="ops")
    op.create_index("ix_ops_ingestion_failures_run_id", "ingestion_failures", ["ingestion_run_id"], schema="ops")
    op.create_index(
        "uq_ops_ingestion_failures_active",
        "ingestion_failures",
        ["ingestion_run_id", "bdns_code", "stage", "error_type"],
        schema="ops",
        unique=True,
        postgresql_where=sa.text("resolved_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_ops_ingestion_failures_active", table_name="ingestion_failures", schema="ops")
    op.drop_index("ix_ops_ingestion_failures_run_id", table_name="ingestion_failures", schema="ops")
    op.drop_index("ix_ops_ingestion_failures_bdns_code", table_name="ingestion_failures", schema="ops")
    op.drop_index("ix_ops_ingestion_failures_unresolved", table_name="ingestion_failures", schema="ops")
    op.drop_table("ingestion_failures", schema="ops")
    op.drop_constraint("ck_ingestion_runs_status", "ingestion_runs", schema="ops", type_="check")
