"""initial schema

Revision ID: 20260413_000001
Revises:
Create Date: 2026-04-13 09:00:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260413_000001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

blood_type_enum = sa.Enum(
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "O+",
    "O-",
    name="blood_type_enum",
    native_enum=False,
)

blood_component_enum = sa.Enum(
    "whole_blood",
    "packed_red_cells",
    "plasma",
    "platelets",
    "cryoprecipitate",
    name="blood_component_enum",
    native_enum=False,
)

blood_bag_status_enum = sa.Enum(
    "collected",
    "tested",
    "available",
    "reserved",
    "issued",
    "transfused",
    "discarded",
    "expired",
    name="blood_bag_status_enum",
    native_enum=False,
)

request_urgency_enum = sa.Enum(
    "routine",
    "urgent",
    "critical",
    name="request_urgency_enum",
    native_enum=False,
)

request_status_enum = sa.Enum(
    "pending",
    "partially_fulfilled",
    "fulfilled",
    "cancelled",
    name="request_status_enum",
    native_enum=False,
)

user_role_enum = sa.Enum(
    "donor",
    "admin",
    "hospital",
    name="user_role_enum",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "donors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("blood_type", blood_type_enum, nullable=False),
        sa.Column("medical_history", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("date_of_birth <= CURRENT_DATE - INTERVAL '18 years'", name="donors_min_age_18"),
        sa.PrimaryKeyConstraint("id", name="pk_donors"),
        sa.UniqueConstraint("email", name="uq_donors_email"),
    )
    op.create_index("ix_donors_blood_type", "donors", ["blood_type"], unique=False)

    op.create_table(
        "hospitals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="hospitals_lat_range"),
        sa.CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="hospitals_lng_range",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_hospitals"),
    )
    op.create_index("ix_hospitals_city", "hospitals", ["city"], unique=False)
    op.create_index("ix_hospitals_name", "hospitals", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("donor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("hospital_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["donor_id"], ["donors.id"], name="fk_users_donor_id_donors", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name="fk_users_hospital_id_hospitals",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("donor_id", name="uq_users_donor_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("hospital_id", name="uq_users_hospital_id"),
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "blood_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_number", sa.String(length=50), nullable=False),
        sa.Column("hospital_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blood_type", blood_type_enum, nullable=False),
        sa.Column("component", blood_component_enum, nullable=False),
        sa.Column("units_requested", sa.Integer(), nullable=False),
        sa.Column("urgency", request_urgency_enum, nullable=False),
        sa.Column(
            "status",
            request_status_enum,
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("units_requested > 0", name="blood_requests_units_positive"),
        sa.CheckConstraint(
            "fulfilled_at IS NULL OR fulfilled_at >= requested_at",
            name="blood_requests_fulfilled_after_requested",
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name="fk_blood_requests_hospital_id_hospitals",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_blood_requests"),
        sa.UniqueConstraint("request_number", name="uq_blood_requests_request_number"),
    )
    op.create_index("ix_blood_requests_hospital_id", "blood_requests", ["hospital_id"], unique=False)
    op.create_index(
        "ix_blood_requests_lookup",
        "blood_requests",
        ["blood_type", "component", "urgency", "status"],
        unique=False,
    )

    op.create_table(
        "blood_bags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bag_number", sa.String(length=50), nullable=False),
        sa.Column("donor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_hospital_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("blood_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("blood_type", blood_type_enum, nullable=False),
        sa.Column("component", blood_component_enum, nullable=False),
        sa.Column("volume_ml", sa.Integer(), nullable=False),
        sa.Column("collection_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expiration_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            blood_bag_status_enum,
            nullable=False,
            server_default=sa.text("'collected'"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("volume_ml > 0", name="blood_bags_volume_positive"),
        sa.CheckConstraint("expiration_date > collection_date", name="blood_bags_exp_after_collection"),
        sa.ForeignKeyConstraint(
            ["blood_request_id"],
            ["blood_requests.id"],
            name="fk_blood_bags_blood_request_id_blood_requests",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["donor_id"], ["donors.id"], name="fk_blood_bags_donor_id_donors", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["storage_hospital_id"],
            ["hospitals.id"],
            name="fk_blood_bags_storage_hospital_id_hospitals",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_blood_bags"),
        sa.UniqueConstraint("bag_number", name="uq_blood_bags_bag_number"),
    )
    op.create_index("ix_blood_bags_blood_request_id", "blood_bags", ["blood_request_id"], unique=False)
    op.create_index("ix_blood_bags_donor_id", "blood_bags", ["donor_id"], unique=False)
    op.create_index("ix_blood_bags_expiration_date", "blood_bags", ["expiration_date"], unique=False)
    op.create_index(
        "ix_blood_bags_inventory_lookup",
        "blood_bags",
        ["blood_type", "component", "status", "expiration_date"],
        unique=False,
    )
    op.create_index("ix_blood_bags_status", "blood_bags", ["status"], unique=False)
    op.create_index("ix_blood_bags_storage_hospital_id", "blood_bags", ["storage_hospital_id"], unique=False)
    op.create_index(
        "ix_blood_bags_storage_status",
        "blood_bags",
        ["storage_hospital_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_blood_bags_storage_status", table_name="blood_bags")
    op.drop_index("ix_blood_bags_storage_hospital_id", table_name="blood_bags")
    op.drop_index("ix_blood_bags_status", table_name="blood_bags")
    op.drop_index("ix_blood_bags_inventory_lookup", table_name="blood_bags")
    op.drop_index("ix_blood_bags_expiration_date", table_name="blood_bags")
    op.drop_index("ix_blood_bags_donor_id", table_name="blood_bags")
    op.drop_index("ix_blood_bags_blood_request_id", table_name="blood_bags")
    op.drop_table("blood_bags")

    op.drop_index("ix_blood_requests_lookup", table_name="blood_requests")
    op.drop_index("ix_blood_requests_hospital_id", table_name="blood_requests")
    op.drop_table("blood_requests")

    op.drop_index("ix_users_role", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_hospitals_name", table_name="hospitals")
    op.drop_index("ix_hospitals_city", table_name="hospitals")
    op.drop_table("hospitals")

    op.drop_index("ix_donors_blood_type", table_name="donors")
    op.drop_table("donors")
