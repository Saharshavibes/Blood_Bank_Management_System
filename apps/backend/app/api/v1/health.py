from pathlib import Path
from typing import Annotated

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter(tags=["system"])
BACKEND_ROOT = Path(__file__).resolve().parents[3]


def _expected_migration_heads() -> set[str]:
    alembic_config = Config(str(BACKEND_ROOT / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    script_directory = ScriptDirectory.from_config(alembic_config)
    return {head for head in script_directory.get_heads() if head}


def _current_migration_versions(db: Session) -> set[str]:
    result = db.execute(text("SELECT version_num FROM alembic_version"))
    return {str(row[0]) for row in result if row and row[0]}


@router.get("/health")
def health_check(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc

    return {"status": "ok"}


@router.get("/health/migration-state")
def migration_state_check(db: Annotated[Session, Depends(get_db)]) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1"))
        expected_heads = _expected_migration_heads()
        current_versions = _current_migration_versions(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database schema migration state unavailable",
        ) from exc

    aligned = bool(expected_heads) and current_versions == expected_heads
    return {
        "status": "ok",
        "migration_state": {
            "aligned": aligned,
            "expected_heads": sorted(expected_heads),
            "current_versions": sorted(current_versions),
        },
    }
