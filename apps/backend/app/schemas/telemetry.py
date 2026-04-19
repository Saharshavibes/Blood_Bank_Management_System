from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DegradedState, DegradedStateSource


class DegradedStateEventCreate(BaseModel):
    source: DegradedStateSource
    state: DegradedState
    message: str | None = Field(default=None, max_length=500)


class DegradedStateEventRead(BaseModel):
    id: UUID
    source: DegradedStateSource
    state: DegradedState
    message: str | None
    user_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)