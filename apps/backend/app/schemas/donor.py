from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import BloodType


class DonorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=30)
    date_of_birth: date
    blood_type: BloodType
    medical_history: str | None = None
    is_active: bool = True


class DonorUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=6, max_length=30)
    date_of_birth: date | None = None
    blood_type: BloodType | None = None
    medical_history: str | None = None
    is_active: bool | None = None


class DonorRead(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    blood_type: BloodType
    medical_history: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
