import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database.session import get_db
from app.models.enums import UserRole
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _resolve_user_from_token(token: str, db: Session) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload missing subject")

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject") from exc

    user = db.get(User, user_uuid)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    return _resolve_user_from_token(token, db)


def get_optional_current_user(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    if not token:
        return None
    payload = decode_access_token(token, raise_error=False)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        return None

    user = db.get(User, user_uuid)
    if user and user.is_active:
        return user
    return None


def require_roles(*roles: UserRole) -> Callable[..., User]:
    def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            allowed_roles = ", ".join(role.value for role in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This resource requires one of these roles: {allowed_roles}",
            )
        return current_user

    return role_checker
