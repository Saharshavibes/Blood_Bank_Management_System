from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DonorTrendPoint(BaseModel):
    month: str
    volume_ml: int
    donations: int


class DonorMilestone(BaseModel):
    title: str
    target_volume_ml: int
    achieved: bool
    achieved_at: datetime | None


class DonorImpactRead(BaseModel):
    donor_id: UUID
    total_volume_ml: int
    total_donations: int
    lives_impacted_estimate: int
    current_badge: str
    next_badge: str | None
    next_milestone_volume_ml: int | None
    trends: list[DonorTrendPoint]
    milestones: list[DonorMilestone]
