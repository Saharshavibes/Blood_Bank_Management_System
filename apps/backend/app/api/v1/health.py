from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
