from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_optional_current_user, require_roles
from app.database.session import get_db
from app.models.degraded_state_event import DegradedStateEvent
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.telemetry import DegradedStateEventCreate, DegradedStateEventRead


router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/degraded-state", response_model=DegradedStateEventRead, status_code=status.HTTP_201_CREATED)
def create_degraded_state_event(
    payload: DegradedStateEventCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> DegradedStateEventRead:
    event = DegradedStateEvent(
        source=payload.source,
        state=payload.state,
        message=payload.message,
        user_id=current_user.id if current_user else None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return DegradedStateEventRead.model_validate(event)


@router.get("/degraded-state", response_model=list[DegradedStateEventRead])
def list_degraded_state_events(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    limit: int = Query(default=100, ge=1, le=500),
) -> list[DegradedStateEventRead]:
    events = db.scalars(
        select(DegradedStateEvent)
        .order_by(DegradedStateEvent.created_at.desc())
        .limit(limit)
    ).all()
    return [DegradedStateEventRead.model_validate(event) for event in events]