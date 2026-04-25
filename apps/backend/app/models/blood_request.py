from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import BloodComponent, BloodType, RequestStatus, RequestUrgency

if TYPE_CHECKING:
    from app.models.blood_bag import BloodBag
    from app.models.hospital import Hospital


class BloodRequest(Base):
    __tablename__ = "blood_requests"
    __table_args__ = (
        CheckConstraint("units_requested > 0", name="blood_requests_units_positive"),
        CheckConstraint("fulfilled_at IS NULL OR fulfilled_at >= requested_at", name="blood_requests_fulfilled_after_requested"),
        Index("ix_blood_requests_lookup", "blood_type", "component", "urgency", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    blood_type: Mapped[BloodType] = mapped_column(
        SAEnum(
            BloodType,
            name="blood_type_enum",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )
    component: Mapped[BloodComponent] = mapped_column(
        SAEnum(
            BloodComponent,
            name="blood_component_enum",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )
    units_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    urgency: Mapped[RequestUrgency] = mapped_column(
        SAEnum(
            RequestUrgency,
            name="request_urgency_enum",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(
            RequestStatus,
            name="request_status_enum",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        server_default=text("'pending'"),
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    hospital: Mapped["Hospital"] = relationship(back_populates="blood_requests")
    blood_bags: Mapped[list["BloodBag"]] = relationship(back_populates="blood_request")
