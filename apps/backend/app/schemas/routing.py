from uuid import UUID

from pydantic import BaseModel

from app.models.enums import RequestUrgency


class RoutingHospitalPoint(BaseModel):
    hospital_id: UUID
    hospital_name: str
    city: str
    latitude: float
    longitude: float


class RoutingCandidate(BaseModel):
    source_hospital_id: UUID
    source_hospital_name: str
    source_city: str
    latitude: float
    longitude: float
    distance_km: float
    available_units: int
    available_volume_ml: int


class RoutingRecommendationResponse(BaseModel):
    request_id: UUID
    request_number: str
    urgency: RequestUrgency
    units_requested: int
    requesting_hospital: RoutingHospitalPoint
    candidates: list[RoutingCandidate]
