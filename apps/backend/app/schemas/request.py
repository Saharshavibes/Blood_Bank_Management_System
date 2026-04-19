from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BloodComponent, BloodType, RequestStatus, RequestUrgency


class BloodRequestCreate(BaseModel):
    request_number: str | None = Field(default=None, min_length=3, max_length=50)
    hospital_id: UUID
    blood_type: BloodType
    component: BloodComponent
    units_requested: int = Field(gt=0)
    urgency: RequestUrgency
    notes: str | None = None


class BloodRequestUpdate(BaseModel):
    blood_type: BloodType | None = None
    component: BloodComponent | None = None
    units_requested: int | None = Field(default=None, gt=0)
    urgency: RequestUrgency | None = None
    status: RequestStatus | None = None
    notes: str | None = None


class BloodRequestRead(BaseModel):
    id: UUID
    request_number: str
    hospital_id: UUID
    blood_type: BloodType
    component: BloodComponent
    units_requested: int
    urgency: RequestUrgency
    status: RequestStatus
    requested_at: datetime
    fulfilled_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
