from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum as SAEnum, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import BloodType

if TYPE_CHECKING:
    from app.models.blood_bag import BloodBag
    from app.models.user import User


class Donor(Base):
    __tablename__ = "donors"
    __table_args__ = (
        CheckConstraint("date_of_birth <= CURRENT_DATE - INTERVAL '18 years'", name="donors_min_age_18"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    blood_type: Mapped[BloodType] = mapped_column(
        SAEnum(BloodType, name="blood_type_enum", native_enum=False, validate_strings=True),
        nullable=False,
        index=True,
    )
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    blood_bags: Mapped[list["BloodBag"]] = relationship(
        back_populates="donor",
        passive_deletes=True,
    )
    user: Mapped["User | None"] = relationship(back_populates="donor", uselist=False)
