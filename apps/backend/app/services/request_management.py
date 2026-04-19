from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.models.blood_request import BloodRequest
from app.models.enums import RequestStatus, UserRole
from app.models.user import User


def generate_request_number(now: datetime | None = None) -> str:
    timestamp = now or datetime.now(UTC)
    return f"REQ-{timestamp.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6].upper()}"


def assert_request_access(current_user: User, request_item: BloodRequest) -> None:
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.HOSPITAL and current_user.hospital_id == request_item.hospital_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this blood request")


def resolve_request_hospital_id(current_user: User, payload_hospital_id: UUID) -> UUID:
    if current_user.role != UserRole.HOSPITAL:
        return payload_hospital_id
    if not current_user.hospital_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No hospital linked to this account")
    return current_user.hospital_id


def apply_request_status_transition(request_item: BloodRequest) -> None:
    if request_item.status == RequestStatus.FULFILLED and request_item.fulfilled_at is None:
        request_item.fulfilled_at = datetime.now(UTC)
        return
    if request_item.status != RequestStatus.FULFILLED:
        request_item.fulfilled_at = None