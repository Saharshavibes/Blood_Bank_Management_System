from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class HospitalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    address: str | None = Field(default=None, min_length=5)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, min_length=6, max_length=30)
    is_active: bool | None = None


class HospitalRead(BaseModel):
    id: UUID
    name: str
    address: str
    city: str
    latitude: float | None
    longitude: float | None
    contact_email: EmailStr
    contact_phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
