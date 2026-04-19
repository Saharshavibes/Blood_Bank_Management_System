from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    issued_at = datetime.now(UTC)
    expire = issued_at + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "typ": "access",
        "iat": issued_at,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt, expire


def decode_access_token(token: str, *, raise_error: bool = True) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("typ") != "access":
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        if not raise_error:
            return None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
