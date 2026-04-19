import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database.session import get_db
from app.models.donor import Donor
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.donor import DonorCreate, DonorRead, DonorUpdate
from app.schemas.impact import DonorImpactRead
from app.services.donor_impact import build_donor_impact

router = APIRouter(prefix="/donors", tags=["donors"])


def _assert_donor_access(current_user: User, donor_id: uuid.UUID) -> None:
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.DONOR and current_user.donor_id == donor_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this donor profile")


@router.post("", response_model=DonorRead, status_code=status.HTTP_201_CREATED)
def create_donor(
    payload: DonorCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> DonorRead:
    existing = db.scalar(select(Donor).where(Donor.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Donor email already exists")

    donor = Donor(**payload.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return DonorRead.model_validate(donor)


@router.get("", response_model=list[DonorRead])
def list_donors(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[DonorRead]:
    donors = db.scalars(select(Donor).offset(skip).limit(limit)).all()
    return [DonorRead.model_validate(item) for item in donors]


@router.get("/{donor_id}", response_model=DonorRead)
def get_donor(
    donor_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DonorRead:
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")

    _assert_donor_access(current_user, donor_id)
    return DonorRead.model_validate(donor)


@router.get("/me/profile", response_model=DonorRead)
def get_my_donor_profile(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.DONOR))],
) -> DonorRead:
    if not current_user.donor_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No donor profile linked to this user")

    donor = db.get(Donor, current_user.donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor profile not found")
    return DonorRead.model_validate(donor)


@router.get("/me/impact", response_model=DonorImpactRead)
def get_my_donor_impact(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.DONOR))],
) -> DonorImpactRead:
    if not current_user.donor_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No donor profile linked to this user")

    donor = db.get(Donor, current_user.donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor profile not found")

    return build_donor_impact(db, donor.id)


@router.get("/{donor_id}/impact", response_model=DonorImpactRead)
def get_donor_impact(
    donor_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DonorImpactRead:
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")

    _assert_donor_access(current_user, donor_id)
    return build_donor_impact(db, donor_id)


@router.put("/{donor_id}", response_model=DonorRead)
def update_donor(
    donor_id: uuid.UUID,
    payload: DonorUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DonorRead:
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")

    _assert_donor_access(current_user, donor_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "email" in update_data:
        existing = db.scalar(select(Donor).where(Donor.email == update_data["email"], Donor.id != donor_id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Donor email already exists")

    if current_user.role == UserRole.DONOR and "is_active" in update_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Donor users cannot modify active state")

    for key, value in update_data.items():
        setattr(donor, key, value)

    db.commit()
    db.refresh(donor)
    return DonorRead.model_validate(donor)


@router.delete("/{donor_id}")
def deactivate_donor(
    donor_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> dict[str, str]:
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")

    donor.is_active = False

    linked_user = db.scalar(select(User).where(User.donor_id == donor_id))
    if linked_user:
        linked_user.is_active = False

    db.commit()
    return {"message": "Donor profile deactivated"}
