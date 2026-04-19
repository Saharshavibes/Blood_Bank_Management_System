from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BloodBagStatus, BloodComponent, BloodType


class BloodBagCreate(BaseModel):
    bag_number: str = Field(min_length=3, max_length=50)
    donor_id: UUID
    blood_type: BloodType
    component: BloodComponent
    volume_ml: int = Field(gt=0)
    collection_date: datetime
    expiration_date: datetime
    status: BloodBagStatus = BloodBagStatus.COLLECTED
    storage_hospital_id: UUID | None = None
    blood_request_id: UUID | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "BloodBagCreate":
        if self.expiration_date <= self.collection_date:
            raise ValueError("expiration_date must be later than collection_date")
        return self


class BloodBagUpdate(BaseModel):
    blood_type: BloodType | None = None
    component: BloodComponent | None = None
    volume_ml: int | None = Field(default=None, gt=0)
    collection_date: datetime | None = None
    expiration_date: datetime | None = None
    status: BloodBagStatus | None = None
    storage_hospital_id: UUID | None = None
    blood_request_id: UUID | None = None


class BloodBagRead(BaseModel):
    id: UUID
    bag_number: str
    donor_id: UUID
    storage_hospital_id: UUID | None
    blood_request_id: UUID | None
    blood_type: BloodType
    component: BloodComponent
    volume_ml: int
    collection_date: datetime
    expiration_date: datetime
    status: BloodBagStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
