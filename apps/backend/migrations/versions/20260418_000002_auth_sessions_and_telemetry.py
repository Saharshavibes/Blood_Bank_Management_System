"""auth sessions and telemetry

Revision ID: 20260418_000002
Revises: 20260413_000001
Create Date: 2026-04-18 13:55:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260418_000002"
down_revision: str | None = "20260413_000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


degraded_state_source_enum = sa.Enum(
    "donor_impact",
    "inventory",
    "urgent_routing",
    name="degraded_state_source_enum",
    native_enum=False,
)

degraded_state_enum = sa.Enum(
    "degraded",
    "recovered",
    name="degraded_state_enum",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_refresh_tokens_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_id"],
            ["refresh_tokens.id"],
            name="fk_refresh_tokens_replaced_by_id_refresh_tokens",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_refresh_tokens"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"], unique=False)
    op.create_index("ix_refresh_tokens_revoked_at", "refresh_tokens", ["revoked_at"], unique=False)
    op.create_index("ix_refresh_tokens_replaced_by_id", "refresh_tokens", ["replaced_by_id"], unique=False)
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    op.create_table(
        "degraded_state_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", degraded_state_source_enum, nullable=False),
        sa.Column("state", degraded_state_enum, nullable=False),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_degraded_state_events_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_degraded_state_events"),
    )
    op.create_index("ix_degraded_state_events_source", "degraded_state_events", ["source"], unique=False)
    op.create_index("ix_degraded_state_events_state", "degraded_state_events", ["state"], unique=False)
    op.create_index("ix_degraded_state_events_user_id", "degraded_state_events", ["user_id"], unique=False)
    op.create_index("ix_degraded_state_events_created_at", "degraded_state_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_degraded_state_events_created_at", table_name="degraded_state_events")
    op.drop_index("ix_degraded_state_events_user_id", table_name="degraded_state_events")
    op.drop_index("ix_degraded_state_events_state", table_name="degraded_state_events")
    op.drop_index("ix_degraded_state_events_source", table_name="degraded_state_events")
    op.drop_table("degraded_state_events")

    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_replaced_by_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_revoked_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
