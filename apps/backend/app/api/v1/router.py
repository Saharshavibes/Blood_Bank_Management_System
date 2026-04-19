from fastapi import APIRouter

from app.api.v1 import auth, donors, health, inventory, requests, telemetry

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(donors.router)
api_router.include_router(inventory.router)
api_router.include_router(requests.router)
api_router.include_router(telemetry.router)
