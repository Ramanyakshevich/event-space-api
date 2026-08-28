from typing import Optional, Sequence

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Booking, Event
from src.schemas.booking import BookingCreate, BookingStatus


class BookingService:
    EVENTS_CACHE_PREFIX = "events:list"

    def __init__(self, db: AsyncSession, redis: Optional[Redis] = None):
        self.db = db
        self.redis = redis

    async def _invalidate_events_cache(self) -> None:
        if not self.redis:
            return
        pattern = f"{self.EVENTS_CACHE_PREFIX}"
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break

    async def create_booking(self, user_id: int, booking_in: BookingCreate) -> Booking:
        stmt = (
            select(Event).where(Event.id == booking_in.event_id).with_for_update
        )
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id={booking_in.event_id} was not found"
            )
        if event.available_seats < booking_in.seats_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No seats available"
            )
        event.available_seats -= booking_in.seats_count
        total_price = event.price * booking_in.seats_count

        booking = Booking(
            user_id=user_id,
            event_id=event.id,
            seats_count=booking_in.seats_count,
            total_price=total_price,
            status=BookingStatus.CONFIRMED
        )
        self.db.add(booking)

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(booking)
        await self._invalidate_events_cache()

        return booking

    async def get_user_bookings(self, user_id: int) -> Sequence[Booking]:
        stmt = (
            select(Booking).where(Booking.user_id == user_id)
            .options(selectinload(Booking.event))
            .order_by(Booking.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def cancel_booking(self, user_id: int, booking_id: int) -> Booking:
        stmt = select(Booking).where(Booking.id == booking_id).with_for_update()
        result = await self.db.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with id={booking_id} was not found"
            )
        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can not cancel someone else booking"
            )
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This booking has already been cancelled"
            )
        event_stmt = select(Event).where(Event.id == booking.event_id).with_for_update()
        event_result = await self.db.execute(event_stmt)
        event = event_result.scalar_one_or_none()

        if event:
            event.available_seats += booking.seats_count

        booking.status = BookingStatus.CANCELLED

        await self.db.commit()
        await self.db.refresh(booking)
        await self._invalidate_events_cache()

        return booking
