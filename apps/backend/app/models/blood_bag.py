from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import BloodBagStatus, BloodComponent, BloodType

if TYPE_CHECKING:
    from app.models.blood_request import BloodRequest
    from app.models.donor import Donor
    from app.models.hospital import Hospital


class BloodBag(Base):
    __tablename__ = "blood_bags"
    __table_args__ = (
        CheckConstraint("volume_ml > 0", name="blood_bags_volume_positive"),
        CheckConstraint("expiration_date > collection_date", name="blood_bags_exp_after_collection"),
        Index("ix_blood_bags_inventory_lookup", "blood_type", "component", "status", "expiration_date"),
        Index("ix_blood_bags_storage_status", "storage_hospital_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bag_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    donor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("donors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    storage_hospital_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    blood_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("blood_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    blood_type: Mapped[BloodType] = mapped_column(
        SAEnum(BloodType, name="blood_type_enum", native_enum=False, validate_strings=True),
        nullable=False,
    )
    component: Mapped[BloodComponent] = mapped_column(
        SAEnum(BloodComponent, name="blood_component_enum", native_enum=False, validate_strings=True),
        nullable=False,
    )
    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    collection_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[BloodBagStatus] = mapped_column(
        SAEnum(BloodBagStatus, name="blood_bag_status_enum", native_enum=False, validate_strings=True),
        nullable=False,
        server_default=text("'collected'"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    donor: Mapped["Donor"] = relationship(back_populates="blood_bags")
    storage_hospital: Mapped["Hospital | None"] = relationship(back_populates="stored_blood_bags")
    blood_request: Mapped["BloodRequest | None"] = relationship(back_populates="blood_bags")
