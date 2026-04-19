from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.security import create_access_token
from app.config import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User


@dataclass(frozen=True)
class SessionTokens:
    access_token: str
    access_expires_at: datetime
    refresh_token: str
    refresh_expires_at: datetime


def _hash_refresh_token(refresh_token: str) -> str:
    return hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        refresh_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def issue_session_tokens(
    db: Session,
    user: User,
    *,
    rotate_from: RefreshToken | None = None,
    issued_at: datetime | None = None,
) -> SessionTokens:
    now = issued_at or datetime.now(UTC)
    access_token, access_expires_at = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = secrets.token_urlsafe(settings.refresh_token_entropy_bytes)
    refresh_expires_at = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh_token(refresh_token),
        issued_at=now,
        expires_at=refresh_expires_at,
    )
    db.add(refresh_record)
    db.flush()

    if rotate_from is not None and rotate_from.revoked_at is None:
        rotate_from.revoked_at = now
        rotate_from.revocation_reason = "rotated"
        rotate_from.replaced_by_id = refresh_record.id

    return SessionTokens(
        access_token=access_token,
        access_expires_at=access_expires_at,
        refresh_token=refresh_token,
        refresh_expires_at=refresh_expires_at,
    )


def get_refresh_token_record(
    db: Session,
    refresh_token: str,
    *,
    lock: bool = False,
) -> RefreshToken | None:
    statement = select(RefreshToken).where(RefreshToken.token_hash == _hash_refresh_token(refresh_token))
    if lock:
        statement = statement.with_for_update()
    return db.scalar(statement)


def revoke_refresh_token(
    refresh_token_record: RefreshToken,
    *,
    reason: str,
    revoked_at: datetime | None = None,
) -> None:
    if refresh_token_record.revoked_at is not None:
        return
    refresh_token_record.revoked_at = revoked_at or datetime.now(UTC)
    refresh_token_record.revocation_reason = reason


def revoke_active_user_refresh_tokens(
    db: Session,
    *,
    user_id: UUID,
    reason: str,
    revoked_at: datetime | None = None,
) -> int:
    now = revoked_at or datetime.now(UTC)
    result = db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(
            revoked_at=now,
            revocation_reason=reason,
        )
    )
    return int(result.rowcount or 0)