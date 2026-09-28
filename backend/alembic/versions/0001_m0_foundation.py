"""M0 foundation: extensions, audit_logs, fee_configs

Creates the two tables M0 owns and enables the extensions M3 searching and M1
addresses depend on, so no later migration has to.

`audit_logs.actor_user_id` and `fee_configs.updated_by` are plain uuid columns
with no foreign key: `users` does not exist until M1, whose migration adds the
constraints.

Revision ID: 0001
Revises: None
Create Date: M0
"""
from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Business configuration read at runtime, never hard-coded in services
# (ADM-04). Values are the ones stated in the SDD and Implementation Plan;
# change them in the database, not here.
#
# Rates are stored in basis points as integers rather than as 0.12, so no
# percentage ever enters a money calculation as a float (ADR-002). The pricing
# service (M4) divides by 10_000 with explicit rounding.
FEE_CONFIG_SEED: tuple[tuple[str, int], ...] = (
    ("commission.rate_bps", 1200),            # Implementation Plan: flat 12%
    ("delivery.base_fee", 2500),              # UGX 2,500 base
    ("delivery.per_km", 1000),                # + UGX 1,000 per km
    ("delivery.min_fee", 3000),               # min UGX 3,000
    ("delivery.max_fee", 15000),              # max UGX 15,000
    ("delivery.rounding", 500),               # rounded to the nearest UGX 500
    ("delivery.rider_share_bps", 8000),       # rider share of the delivery fee: 80%
    ("timers.seller_response_minutes", 10),
    ("timers.payment_window_minutes", 10),
    ("timers.rider_offer_seconds", 45),
)

# audit_logs and ledger_entries are append-only (Database Design section 2.6).
# In development the application user owns the table, so REVOKE is inert; a
# trigger holds the rule wherever the code runs.
APPEND_ONLY_FUNCTION = """
CREATE OR REPLACE FUNCTION kleim_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION '% is append-only', TG_TABLE_NAME
        USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    # PostGIS for addresses, store locations and distance (ADR-008, M1/M3);
    # pg_trgm for typo-tolerant search (M3).
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("before", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # statement_timestamp(), not now(): now() is transaction time, so two
        # entries written by the same request would share a timestamp and the
        # audit trail would have no stable order.
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("statement_timestamp()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_target", "audit_logs", ["target_type", "target_id"])
    op.create_index(
        "ix_audit_logs_actor_user_id_created_at", "audit_logs", ["actor_user_id", "created_at"]
    )

    op.execute(APPEND_ONLY_FUNCTION)
    op.execute(
        """
        CREATE TRIGGER audit_logs_append_only
        BEFORE UPDATE OR DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION kleim_append_only()
        """
    )

    op.create_table(
        "fee_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_fee_configs"),
    )
    # One active row per key at a given time; history is kept by inserting a new
    # row with a later effective_from, so the unique index spans both columns.
    op.create_unique_constraint(
        "uq_fee_configs_key_effective_from", "fee_configs", ["key", "effective_from"]
    )
    op.create_index("ix_fee_configs_key", "fee_configs", ["key"])

    fee_configs = sa.table(
        "fee_configs",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String),
        sa.column("value", postgresql.JSONB),
    )
    op.bulk_insert(
        fee_configs,
        [
            {"id": uuid.uuid4(), "key": key, "value": value}
            for key, value in FEE_CONFIG_SEED
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_fee_configs_key", table_name="fee_configs")
    op.drop_constraint("uq_fee_configs_key_effective_from", "fee_configs", type_="unique")
    op.drop_table("fee_configs")

    op.execute("DROP TRIGGER IF EXISTS audit_logs_append_only ON audit_logs")
    op.drop_index("ix_audit_logs_actor_user_id_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_target", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.execute("DROP FUNCTION IF EXISTS kleim_append_only()")

    # Extensions are left in place: other databases on the same cluster may rely
    # on them, and re-creating them is idempotent.
