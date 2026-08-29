from typing import List
from fastapi import APIRouter, status

from src.api.dependencies import BookingServiceDep, CurrentUserDep
from src.schemas.booking import BookingRead, BookingCreate

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
        booking_in: BookingCreate,
        booking_service: BookingServiceDep,
        current_user: CurrentUserDep
):
    return await booking_service.create_booking(user_id=current_user.id, booking_in=booking_in)

@router.get("/my", response_model=List[BookingRead])
async def get_my_bookings(
        booking_service: BookingServiceDep,
        current_user: CurrentUserDep
):
    return await booking_service.get_user_bookings(user_id=current_user.id)

@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
        booking_service: BookingServiceDep,
        current_user: CurrentUserDep,
        booking_id: int
):
    return await booking_service.cancel_booking(user_id=current_user.id, booking_id=booking_id)