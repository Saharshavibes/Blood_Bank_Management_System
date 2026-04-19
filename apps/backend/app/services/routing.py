from __future__ import annotations

from datetime import UTC, datetime
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.blood_bag import BloodBag
from app.models.blood_request import BloodRequest
from app.models.enums import BloodBagStatus
from app.models.hospital import Hospital
from app.schemas.routing import RoutingCandidate, RoutingHospitalPoint, RoutingRecommendationResponse


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    d_lat = lat2_rad - lat1_rad
    d_lon = lon2_rad - lon1_rad

    a = sin(d_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return earth_radius_km * c


def build_nearest_routing_recommendation(
    db: Session,
    request_item: BloodRequest,
    requesting_hospital: Hospital,
    *,
    max_results: int = 5,
) -> RoutingRecommendationResponse:
    if requesting_hospital.latitude is None or requesting_hospital.longitude is None:
        raise ValueError("Requesting hospital requires latitude and longitude for routing")

    now_utc = datetime.now(UTC)

    query = (
        select(
            Hospital.id.label("source_hospital_id"),
            Hospital.name.label("source_hospital_name"),
            Hospital.city.label("source_city"),
            Hospital.latitude.label("latitude"),
            Hospital.longitude.label("longitude"),
            func.count(BloodBag.id).label("available_units"),
            func.coalesce(func.sum(BloodBag.volume_ml), 0).label("available_volume_ml"),
        )
        .join(BloodBag, BloodBag.storage_hospital_id == Hospital.id)
        .where(
            Hospital.is_active.is_(True),
            Hospital.id != requesting_hospital.id,
            BloodBag.status == BloodBagStatus.AVAILABLE,
            BloodBag.blood_type == request_item.blood_type,
            BloodBag.component == request_item.component,
            BloodBag.expiration_date > now_utc,
        )
        .group_by(Hospital.id)
    )

    raw_rows = db.execute(query).mappings().all()

    origin_lat = float(requesting_hospital.latitude)
    origin_lng = float(requesting_hospital.longitude)

    candidates: list[RoutingCandidate] = []
    for row in raw_rows:
        row_data = dict(row)
        if row_data["latitude"] is None or row_data["longitude"] is None:
            continue

        source_lat = float(row_data["latitude"])
        source_lng = float(row_data["longitude"])
        distance_km = haversine_distance_km(origin_lat, origin_lng, source_lat, source_lng)

        candidates.append(
            RoutingCandidate(
                source_hospital_id=row_data["source_hospital_id"],
                source_hospital_name=row_data["source_hospital_name"],
                source_city=row_data["source_city"],
                latitude=source_lat,
                longitude=source_lng,
                distance_km=round(distance_km, 2),
                available_units=int(row_data["available_units"]),
                available_volume_ml=int(row_data["available_volume_ml"]),
            )
        )

    candidates.sort(key=lambda item: item.distance_km)
    limited_candidates = candidates[:max_results]

    return RoutingRecommendationResponse(
        request_id=request_item.id,
        request_number=request_item.request_number,
        urgency=request_item.urgency,
        units_requested=request_item.units_requested,
        requesting_hospital=RoutingHospitalPoint(
            hospital_id=requesting_hospital.id,
            hospital_name=requesting_hospital.name,
            city=requesting_hospital.city,
            latitude=origin_lat,
            longitude=origin_lng,
        ),
        candidates=limited_candidates,
    )
