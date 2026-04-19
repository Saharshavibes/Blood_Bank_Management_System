from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_optional_current_user
from app.auth.security import create_access_token, get_password_hash, verify_password
from app.database.session import get_db
from app.models.donor import Donor
from app.models.enums import UserRole
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.auth import (
    AdminRegisterRequest,
    AuthMessage,
    AuthStatus,
    DonorRegisterRequest,
    HospitalRegisterRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRead,
)
from app.services.auth_sessions import (
    get_refresh_token_record,
    issue_session_tokens,
    revoke_active_user_refresh_tokens,
    revoke_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_token_response(
    db: Session,
    user: User,
    *,
    rotate_from=None,
    issued_at: datetime | None = None,
) -> TokenResponse:
    session_tokens = issue_session_tokens(db, user, rotate_from=rotate_from, issued_at=issued_at)
    return TokenResponse(
        access_token=session_tokens.access_token,
        expires_at=session_tokens.access_expires_at,
        refresh_token=session_tokens.refresh_token,
        refresh_expires_at=session_tokens.refresh_expires_at,
        user=UserRead.model_validate(user),
    )


@router.post("/register/donor", response_model=AuthMessage, status_code=status.HTTP_201_CREATED)
def register_donor(
    payload: DonorRegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthMessage:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists")

    existing_donor = db.scalar(select(Donor).where(Donor.email == payload.email))
    if existing_donor:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Donor email already exists")

    donor = Donor(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        blood_type=payload.blood_type,
        medical_history=payload.medical_history,
        is_active=True,
    )

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=UserRole.DONOR,
        donor=donor,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthMessage(message="Donor registration successful", user=UserRead.model_validate(user))


@router.post("/register/hospital", response_model=AuthMessage, status_code=status.HTTP_201_CREATED)
def register_hospital(
    payload: HospitalRegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthMessage:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists")

    hospital = Hospital(
        name=payload.name,
        address=payload.address,
        city=payload.city,
        latitude=payload.latitude,
        longitude=payload.longitude,
        contact_email=payload.email,
        contact_phone=payload.contact_phone,
        is_active=True,
    )

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=UserRole.HOSPITAL,
        hospital=hospital,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthMessage(message="Hospital registration successful", user=UserRead.model_validate(user))


@router.post("/register/admin", response_model=AuthMessage, status_code=status.HTTP_201_CREATED)
def register_admin(
    payload: AdminRegisterRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> AuthMessage:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists")

    admin_count = db.scalar(select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)) or 0
    if admin_count > 0:
        if current_user is None or current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only an admin can create another admin",
            )

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=UserRole.ADMIN,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthMessage(message="Admin registration successful", user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    token_response = _build_token_response(db, user)
    db.commit()
    return token_response


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshTokenRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    now = datetime.now(UTC)
    refresh_record = get_refresh_token_record(db, payload.refresh_token, lock=True)
    if refresh_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired",
        )

    if refresh_record.revoked_at is not None:
        if refresh_record.replaced_by_id is not None:
            revoke_active_user_refresh_tokens(
                db,
                user_id=refresh_record.user_id,
                reason="refresh_token_reuse_detected",
                revoked_at=now,
            )
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired",
        )

    if refresh_record.expires_at <= now:
        revoke_refresh_token(refresh_record, reason="expired", revoked_at=now)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired",
        )

    user = refresh_record.user
    if user is None or not user.is_active:
        revoke_refresh_token(refresh_record, reason="user_inactive", revoked_at=now)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired",
        )

    token_response = _build_token_response(db, user, rotate_from=refresh_record, issued_at=now)
    db.commit()
    return token_response


@router.post("/logout", response_model=AuthStatus)
def logout(
    payload: LogoutRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthStatus:
    refresh_record = get_refresh_token_record(db, payload.refresh_token, lock=True)
    if refresh_record is not None and refresh_record.revoked_at is None:
        revoke_refresh_token(refresh_record, reason="logout")
        db.commit()
    return AuthStatus(message="Session ended")


@router.post("/logout-all", response_model=AuthStatus)
def logout_all(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AuthStatus:
    revoke_active_user_refresh_tokens(db, user_id=current_user.id, reason="logout_all")
    db.commit()
    return AuthStatus(message="All sessions ended")


@router.get("/me", response_model=UserRead)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead.model_validate(current_user)
