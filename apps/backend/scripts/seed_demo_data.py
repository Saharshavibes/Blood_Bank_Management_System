from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.database.session import SessionLocal
from app.models.blood_bag import BloodBag
from app.models.blood_request import BloodRequest
from app.models.degraded_state_event import DegradedStateEvent
from app.models.donor import Donor
from app.models.enums import (
    BloodBagStatus,
    BloodComponent,
    BloodType,
    DegradedState,
    DegradedStateSource,
    RequestStatus,
    RequestUrgency,
    UserRole,
)
from app.models.hospital import Hospital
from app.models.user import User

ADMIN_EMAIL = "saharshabattula41@gmail.com"
ADMIN_PASSWORD = "<Blood_bank@123>"


def ensure_admin_user(db: Session) -> tuple[User, bool]:
    admin_user = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
    created = False

    if admin_user is None:
        admin_user = User(
            email=ADMIN_EMAIL,
            password_hash=get_password_hash(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()
        created = True
    else:
        admin_user.role = UserRole.ADMIN
        admin_user.password_hash = get_password_hash(ADMIN_PASSWORD)
        admin_user.is_active = True

    return admin_user, created


def ensure_hospitals(db: Session) -> tuple[dict[str, Hospital], int]:
    records = [
        {
            "email": "hospital.alpha@bloodbank.local",
            "password": "HospitalAlpha123!",
            "name": "Central City Hospital",
            "address": "14 Care Avenue",
            "city": "Metropolis",
            "latitude": Decimal("40.712776"),
            "longitude": Decimal("-74.005974"),
            "contact_phone": "+1-212-555-0101",
        },
        {
            "email": "hospital.beta@bloodbank.local",
            "password": "HospitalBeta123!",
            "name": "Northside Medical Center",
            "address": "88 Relief Street",
            "city": "Gotham",
            "latitude": Decimal("34.052235"),
            "longitude": Decimal("-118.243683"),
            "contact_phone": "+1-310-555-0199",
        },
    ]

    created_count = 0
    hospital_map: dict[str, Hospital] = {}

    for item in records:
        hospital = db.scalar(select(Hospital).where(Hospital.contact_email == item["email"]))
        if hospital is None:
            hospital = Hospital(
                name=item["name"],
                address=item["address"],
                city=item["city"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                contact_email=item["email"],
                contact_phone=item["contact_phone"],
                is_active=True,
            )
            db.add(hospital)
            db.flush()
            created_count += 1
        else:
            hospital.name = item["name"]
            hospital.address = item["address"]
            hospital.city = item["city"]
            hospital.latitude = item["latitude"]
            hospital.longitude = item["longitude"]
            hospital.contact_phone = item["contact_phone"]
            hospital.is_active = True

        user = db.scalar(select(User).where(User.email == item["email"]))
        if user is None:
            user = User(
                email=item["email"],
                password_hash=get_password_hash(item["password"]),
                role=UserRole.HOSPITAL,
                hospital_id=hospital.id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            created_count += 1
        else:
            user.role = UserRole.HOSPITAL
            user.password_hash = get_password_hash(item["password"])
            user.hospital_id = hospital.id
            user.is_active = True

        hospital_map[item["email"]] = hospital

    return hospital_map, created_count


def ensure_donors(db: Session) -> tuple[dict[str, Donor], int]:
    records = [
        {
            "email": "donor.alex@bloodbank.local",
            "password": "DonorAlex123!",
            "full_name": "Alex Morgan",
            "phone": "+1-202-555-0144",
            "date_of_birth": date(1991, 5, 12),
            "blood_type": BloodType.O_POS,
            "medical_history": "No known chronic disease",
        },
        {
            "email": "donor.bianca@bloodbank.local",
            "password": "DonorBianca123!",
            "full_name": "Bianca Flores",
            "phone": "+1-202-555-0145",
            "date_of_birth": date(1988, 11, 3),
            "blood_type": BloodType.A_NEG,
            "medical_history": "Mild seasonal allergy",
        },
        {
            "email": "donor.carter@bloodbank.local",
            "password": "DonorCarter123!",
            "full_name": "Carter Singh",
            "phone": "+1-202-555-0146",
            "date_of_birth": date(1994, 2, 21),
            "blood_type": BloodType.B_POS,
            "medical_history": "No transfusion history",
        },
    ]

    created_count = 0
    donor_map: dict[str, Donor] = {}

    for item in records:
        donor = db.scalar(select(Donor).where(Donor.email == item["email"]))
        if donor is None:
            donor = Donor(
                full_name=item["full_name"],
                email=item["email"],
                phone=item["phone"],
                date_of_birth=item["date_of_birth"],
                blood_type=item["blood_type"],
                medical_history=item["medical_history"],
                is_active=True,
            )
            db.add(donor)
            db.flush()
            created_count += 1
        else:
            donor.full_name = item["full_name"]
            donor.phone = item["phone"]
            donor.date_of_birth = item["date_of_birth"]
            donor.blood_type = item["blood_type"]
            donor.medical_history = item["medical_history"]
            donor.is_active = True

        user = db.scalar(select(User).where(User.email == item["email"]))
        if user is None:
            user = User(
                email=item["email"],
                password_hash=get_password_hash(item["password"]),
                role=UserRole.DONOR,
                donor_id=donor.id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            created_count += 1
        else:
            user.role = UserRole.DONOR
            user.password_hash = get_password_hash(item["password"])
            user.donor_id = donor.id
            user.is_active = True

        donor_map[item["email"]] = donor

    return donor_map, created_count


def ensure_blood_bags(db: Session, donors: dict[str, Donor], hospitals: dict[str, Hospital]) -> int:
    donor_keys = list(donors.keys())
    hospital_keys = list(hospitals.keys())
    blood_types = [
        BloodType.O_POS,
        BloodType.O_NEG,
        BloodType.A_POS,
        BloodType.A_NEG,
        BloodType.B_POS,
        BloodType.B_NEG,
        BloodType.AB_POS,
        BloodType.AB_NEG,
    ]
    components = [
        BloodComponent.PACKED_RED_CELLS,
        BloodComponent.PLASMA,
        BloodComponent.PLATELETS,
        BloodComponent.WHOLE_BLOOD,
    ]

    now = datetime.now(UTC)
    created_count = 0

    for index in range(18):
        bag_number = f"DEMO-BAG-{index + 1:04d}"
        donor = donors[donor_keys[index % len(donor_keys)]]
        hospital = hospitals[hospital_keys[index % len(hospital_keys)]]
        blood_type = blood_types[index % len(blood_types)]
        component = components[index % len(components)]
        status = BloodBagStatus.RESERVED if index % 4 == 0 else BloodBagStatus.AVAILABLE
        collection_date = now - timedelta(days=2 + index)
        expiration_date = collection_date + timedelta(days=35 + (index % 6))
        volume_ml = 320 + ((index % 4) * 40)

        bag = db.scalar(select(BloodBag).where(BloodBag.bag_number == bag_number))
        if bag is None:
            bag = BloodBag(
                bag_number=bag_number,
                donor_id=donor.id,
                storage_hospital_id=hospital.id,
                blood_request_id=None,
                blood_type=blood_type,
                component=component,
                volume_ml=volume_ml,
                collection_date=collection_date,
                expiration_date=expiration_date,
                status=status,
            )
            db.add(bag)
            created_count += 1
        else:
            bag.donor_id = donor.id
            bag.storage_hospital_id = hospital.id
            bag.blood_request_id = None
            bag.blood_type = blood_type
            bag.component = component
            bag.volume_ml = volume_ml
            bag.collection_date = collection_date
            bag.expiration_date = expiration_date
            bag.status = status

    db.flush()
    return created_count


def ensure_blood_requests(db: Session, hospitals: dict[str, Hospital]) -> int:
    now = datetime.now(UTC)
    records = [
        {
            "request_number": "DEMO-REQ-0001",
            "hospital_email": "hospital.alpha@bloodbank.local",
            "blood_type": BloodType.A_POS,
            "component": BloodComponent.PACKED_RED_CELLS,
            "units_requested": 3,
            "urgency": RequestUrgency.ROUTINE,
            "status": RequestStatus.PENDING,
            "requested_at": now - timedelta(hours=30),
            "fulfilled_at": None,
            "notes": "Routine replenishment for surgery schedule",
        },
        {
            "request_number": "DEMO-REQ-0002",
            "hospital_email": "hospital.beta@bloodbank.local",
            "blood_type": BloodType.O_NEG,
            "component": BloodComponent.PACKED_RED_CELLS,
            "units_requested": 2,
            "urgency": RequestUrgency.URGENT,
            "status": RequestStatus.PENDING,
            "requested_at": now - timedelta(hours=12),
            "fulfilled_at": None,
            "notes": "Emergency trauma intake request",
        },
        {
            "request_number": "DEMO-REQ-0003",
            "hospital_email": "hospital.alpha@bloodbank.local",
            "blood_type": BloodType.B_POS,
            "component": BloodComponent.PLASMA,
            "units_requested": 4,
            "urgency": RequestUrgency.ROUTINE,
            "status": RequestStatus.FULFILLED,
            "requested_at": now - timedelta(days=2, hours=6),
            "fulfilled_at": now - timedelta(days=2, hours=2),
            "notes": "Oncology support batch fulfilled",
        },
        {
            "request_number": "DEMO-REQ-0004",
            "hospital_email": "hospital.beta@bloodbank.local",
            "blood_type": BloodType.AB_NEG,
            "component": BloodComponent.PLATELETS,
            "units_requested": 1,
            "urgency": RequestUrgency.CRITICAL,
            "status": RequestStatus.FULFILLED,
            "requested_at": now - timedelta(days=1, hours=8),
            "fulfilled_at": now - timedelta(days=1, hours=5),
            "notes": "Critical neonatal platelet support completed",
        },
        {
            "request_number": "DEMO-REQ-0005",
            "hospital_email": "hospital.alpha@bloodbank.local",
            "blood_type": BloodType.O_POS,
            "component": BloodComponent.WHOLE_BLOOD,
            "units_requested": 5,
            "urgency": RequestUrgency.CRITICAL,
            "status": RequestStatus.PARTIALLY_FULFILLED,
            "requested_at": now - timedelta(hours=20),
            "fulfilled_at": None,
            "notes": "Mass casualty response still in progress",
        },
    ]

    created_count = 0

    for item in records:
        hospital = hospitals[item["hospital_email"]]
        request = db.scalar(select(BloodRequest).where(BloodRequest.request_number == item["request_number"]))
        if request is None:
            request = BloodRequest(
                request_number=item["request_number"],
                hospital_id=hospital.id,
                blood_type=item["blood_type"],
                component=item["component"],
                units_requested=item["units_requested"],
                urgency=item["urgency"],
                status=item["status"],
                requested_at=item["requested_at"],
                fulfilled_at=item["fulfilled_at"],
                notes=item["notes"],
            )
            db.add(request)
            created_count += 1
        else:
            request.hospital_id = hospital.id
            request.blood_type = item["blood_type"]
            request.component = item["component"]
            request.units_requested = item["units_requested"]
            request.urgency = item["urgency"]
            request.status = item["status"]
            request.requested_at = item["requested_at"]
            request.fulfilled_at = item["fulfilled_at"]
            request.notes = item["notes"]

    db.flush()
    return created_count


def ensure_degraded_state_events(db: Session, admin_user: User) -> int:
    records = [
        {
            "source": DegradedStateSource.INVENTORY,
            "state": DegradedState.DEGRADED,
            "message": "Inventory read latency crossed threshold",
        },
        {
            "source": DegradedStateSource.INVENTORY,
            "state": DegradedState.RECOVERED,
            "message": "Inventory API recovered to normal",
        },
        {
            "source": DegradedStateSource.DONOR_IMPACT,
            "state": DegradedState.DEGRADED,
            "message": "Donor impact analytics running in fallback mode",
        },
        {
            "source": DegradedStateSource.URGENT_ROUTING,
            "state": DegradedState.RECOVERED,
            "message": "Urgent routing service recovered after timeout spike",
        },
    ]

    created_count = 0

    for item in records:
        existing = db.scalar(
            select(DegradedStateEvent).where(
                DegradedStateEvent.source == item["source"],
                DegradedStateEvent.state == item["state"],
                DegradedStateEvent.message == item["message"],
            )
        )
        if existing is None:
            event = DegradedStateEvent(
                source=item["source"],
                state=item["state"],
                message=item["message"],
                user_id=admin_user.id,
            )
            db.add(event)
            created_count += 1

    db.flush()
    return created_count


def main() -> None:
    db = SessionLocal()

    try:
        admin_user, admin_created = ensure_admin_user(db)
        hospitals, hospital_created = ensure_hospitals(db)
        donors, donor_created = ensure_donors(db)
        blood_bag_created = ensure_blood_bags(db, donors, hospitals)
        request_created = ensure_blood_requests(db, hospitals)
        telemetry_created = ensure_degraded_state_events(db, admin_user)
        db.commit()

        print("Demo seed complete")
        print(f"admin_created={admin_created}")
        print(f"hospitals_or_hospital_users_created={hospital_created}")
        print(f"donors_or_donor_users_created={donor_created}")
        print(f"blood_bags_created={blood_bag_created}")
        print(f"blood_requests_created={request_created}")
        print(f"telemetry_events_created={telemetry_created}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
