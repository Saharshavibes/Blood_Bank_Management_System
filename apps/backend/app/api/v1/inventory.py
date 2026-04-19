import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.session import get_db
from app.models.blood_bag import BloodBag
from app.models.blood_request import BloodRequest
from app.models.donor import Donor
from app.models.enums import BloodBagStatus, BloodComponent, BloodType, UserRole
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.inventory import BloodBagCreate, BloodBagRead, BloodBagUpdate

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/bags", response_model=BloodBagRead, status_code=status.HTTP_201_CREATED)
def add_blood_bag(
    payload: BloodBagCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> BloodBagRead:
    existing = db.scalar(select(BloodBag).where(BloodBag.bag_number == payload.bag_number))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bag number already exists")

    donor = db.get(Donor, payload.donor_id)
    if donor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")

    if payload.storage_hospital_id:
        hospital = db.get(Hospital, payload.storage_hospital_id)
        if hospital is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage hospital not found")

    if payload.blood_request_id:
        request = db.get(BloodRequest, payload.blood_request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found")

    blood_bag = BloodBag(**payload.model_dump())
    db.add(blood_bag)
    db.commit()
    db.refresh(blood_bag)
    return BloodBagRead.model_validate(blood_bag)


@router.get("/bags", response_model=list[BloodBagRead])
def list_blood_bags(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL))],
    blood_type: BloodType | None = Query(default=None),
    component: BloodComponent | None = Query(default=None),
    status_filter: BloodBagStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[BloodBagRead]:
    query = select(BloodBag)

    if current_user.role == UserRole.HOSPITAL:
        if not current_user.hospital_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No hospital linked to this account")
        query = query.where(BloodBag.storage_hospital_id == current_user.hospital_id)

    if blood_type:
        query = query.where(BloodBag.blood_type == blood_type)
    if component:
        query = query.where(BloodBag.component == component)
    if status_filter:
        query = query.where(BloodBag.status == status_filter)

    bags = db.scalars(query.order_by(BloodBag.expiration_date).offset(skip).limit(limit)).all()
    return [BloodBagRead.model_validate(item) for item in bags]


@router.get("/bags/{bag_id}", response_model=BloodBagRead)
def get_blood_bag(
    bag_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL))],
) -> BloodBagRead:
    blood_bag = db.get(BloodBag, bag_id)
    if not blood_bag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood bag not found")

    if current_user.role == UserRole.HOSPITAL and blood_bag.storage_hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this blood bag")

    return BloodBagRead.model_validate(blood_bag)


@router.get("/scan/{bag_number}", response_model=BloodBagRead)
def scan_bag_by_number(
    bag_number: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL))],
) -> BloodBagRead:
    blood_bag = db.scalar(select(BloodBag).where(BloodBag.bag_number == bag_number))
    if not blood_bag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood bag not found")

    if current_user.role == UserRole.HOSPITAL and blood_bag.storage_hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this blood bag")

    return BloodBagRead.model_validate(blood_bag)


@router.patch("/bags/{bag_id}", response_model=BloodBagRead)
def update_blood_bag(
    bag_id: uuid.UUID,
    payload: BloodBagUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.HOSPITAL))],
) -> BloodBagRead:
    blood_bag = db.get(BloodBag, bag_id)
    if not blood_bag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood bag not found")

    if current_user.role == UserRole.HOSPITAL and blood_bag.storage_hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this blood bag")

    update_data = payload.model_dump(exclude_unset=True)

    if "storage_hospital_id" in update_data and update_data["storage_hospital_id"] is not None:
        hospital = db.get(Hospital, update_data["storage_hospital_id"])
        if hospital is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage hospital not found")

    if "blood_request_id" in update_data and update_data["blood_request_id"] is not None:
        request = db.get(BloodRequest, update_data["blood_request_id"])
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found")

    new_collection_date = update_data.get("collection_date", blood_bag.collection_date)
    new_expiration_date = update_data.get("expiration_date", blood_bag.expiration_date)
    if new_expiration_date <= new_collection_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expiration_date must be later than collection_date",
        )

    for key, value in update_data.items():
        setattr(blood_bag, key, value)

    db.commit()
    db.refresh(blood_bag)
    return BloodBagRead.model_validate(blood_bag)


@router.delete("/bags/{bag_id}")
def delete_blood_bag(
    bag_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> dict[str, str]:
    blood_bag = db.get(BloodBag, bag_id)
    if not blood_bag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood bag not found")

    if blood_bag.blood_request_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a blood bag linked to a request",
        )

    if blood_bag.status in {BloodBagStatus.ISSUED, BloodBagStatus.TRANSFUSED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Issued or transfused bags cannot be deleted",
        )

    db.delete(blood_bag)
    db.commit()
    return {"message": "Blood bag deleted"}
