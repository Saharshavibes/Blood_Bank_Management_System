from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.session import get_db
from app.models.blood_request import BloodRequest
from app.models.enums import RequestStatus, RequestUrgency, UserRole
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.request import BloodRequestCreate, BloodRequestRead, BloodRequestUpdate
from app.schemas.routing import RoutingRecommendationResponse
from app.services.request_management import (
    apply_request_status_transition,
    assert_request_access,
    generate_request_number,
    resolve_request_hospital_id,
)
from app.services.routing import build_nearest_routing_recommendation

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=BloodRequestRead, status_code=status.HTTP_201_CREATED)
def create_blood_request(
    payload: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL)),
) -> BloodRequestRead:
    hospital_id = resolve_request_hospital_id(current_user, payload.hospital_id)

    hospital = db.get(Hospital, hospital_id)
    if hospital is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    request_number = payload.request_number or generate_request_number()
    duplicate = db.scalar(select(BloodRequest).where(BloodRequest.request_number == request_number))
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Request number already exists")

    request_item = BloodRequest(
        request_number=request_number,
        hospital_id=hospital_id,
        blood_type=payload.blood_type,
        component=payload.component,
        units_requested=payload.units_requested,
        urgency=payload.urgency,
        status=RequestStatus.PENDING,
        notes=payload.notes,
    )

    db.add(request_item)
    db.commit()
    db.refresh(request_item)
    return BloodRequestRead.model_validate(request_item)


@router.get("", response_model=list[BloodRequestRead])
def list_blood_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL)),
    status_filter: RequestStatus | None = Query(default=None, alias="status"),
    urgency: RequestUrgency | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[BloodRequestRead]:
    query = select(BloodRequest)

    if current_user.role == UserRole.HOSPITAL:
        if not current_user.hospital_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No hospital linked to this account")
        query = query.where(BloodRequest.hospital_id == current_user.hospital_id)

    if status_filter:
        query = query.where(BloodRequest.status == status_filter)
    if urgency:
        query = query.where(BloodRequest.urgency == urgency)

    request_items = db.scalars(query.order_by(BloodRequest.requested_at.desc()).offset(skip).limit(limit)).all()
    return [BloodRequestRead.model_validate(item) for item in request_items]


@router.get("/{request_id}", response_model=BloodRequestRead)
def get_blood_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL)),
) -> BloodRequestRead:
    request_item = db.get(BloodRequest, request_id)
    if not request_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found")

    assert_request_access(current_user, request_item)
    return BloodRequestRead.model_validate(request_item)


@router.get("/{request_id}/nearest-banks", response_model=RoutingRecommendationResponse)
def get_nearest_blood_banks_for_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL)),
    max_results: int = Query(default=5, ge=1, le=20),
) -> RoutingRecommendationResponse:
    request_item = db.get(BloodRequest, request_id)
    if not request_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found")

    assert_request_access(current_user, request_item)

    if request_item.urgency == RequestUrgency.ROUTINE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nearest routing is only available for urgent or critical requests",
        )

    requesting_hospital = db.get(Hospital, request_item.hospital_id)
    if requesting_hospital is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requesting hospital not found")

    try:
        return build_nearest_routing_recommendation(
            db,
            request_item,
            requesting_hospital,
            max_results=max_results,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{request_id}", response_model=BloodRequestRead)
def update_blood_request(
    request_id: UUID,
    payload: BloodRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL)),
) -> BloodRequestRead:
    request_item = db.get(BloodRequest, request_id)
    if not request_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found")

    assert_request_access(current_user, request_item)

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_item, key, value)

    apply_request_status_transition(request_item)

    db.commit()
    db.refresh(request_item)
    return BloodRequestRead.model_validate(request_item)


@router.delete("/{request_id}")
def delete_blood_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL)),
) -> dict[str, str]:
    request_item = db.get(BloodRequest, request_id)
    if not request_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found")

    assert_request_access(current_user, request_item)

    db.delete(request_item)
    db.commit()
    return {"message": "Blood request deleted"}
