from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.events import router as events_router
from src.api.v1.bookings import router as bookings_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(bookings_router)