import asyncio
from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import NullPool

from src.core.config import settings
from src.models import Booking
from src.schemas.booking import BookingStatus
from src.tasks.worker import celery_app

logger = logging.getLogger(__name__)


async def _cancel_expired_booking_async() -> int:
    expiration_threshold = (
        datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=15)
    )
    cancelled_count = 0

    task_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        future=True,
    )
    task_session_maker = async_sessionmaker(
        bind=task_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with task_session_maker() as session:
            async with session.begin():
                stmt = (
                    select(Booking)
                    .where(
                        Booking.status == BookingStatus.PENDING,
                        Booking.created_at <= expiration_threshold,
                    )
                    .options(selectinload(Booking.event))
                    .with_for_update()
                )
                result = await session.execute(stmt)
                expired_bookings = result.scalars().all()

                if not expired_bookings:
                    return 0

                for booking in expired_bookings:
                    if booking.event:
                        booking.event.available_seats += booking.tickets_count
                    booking.status = BookingStatus.CANCELLED
                    cancelled_count += 1
                    logger.info(
                        f"Booking #{booking.id} was cancelled. Number of returned tickets: {booking.tickets_count}"
                    )
    finally:
        await task_engine.dispose()

    return cancelled_count


@celery_app.task(name="cancel_expired_bookings")
def cancel_expired_bookings():
    logger.info("Checking expired bookings")
    cancelled_count = asyncio.run(_cancel_expired_booking_async())
    logger.info(f"END. Cancelled bookings: {cancelled_count}")
    return {"cancelled_count": cancelled_count}