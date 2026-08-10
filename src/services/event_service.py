from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event
from src.schemas.event import EventCreate, EventUpdate


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, skip: int = 0, limit: int = 100) -> Sequence[Event]:
        stmt = (
            select(Event)
            .offset(skip)
            .limit(limit)
            .order_by(Event.event_date.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, event_id: int) -> Event:
        stmt = select(Event).where(Event.id == event_id)
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id={id} not found"
            )
        return event

    async def create(self, event_in: EventCreate) -> Event:
        event_data = event_in.model_dump()
        event_data["available_seats"] = event_in.total_seats

        new_event = Event(**event_data)
        await self.db.commit()
        await self.db.refresh(new_event)
        return new_event

    async def update(self, event_id: int, event_in: EventUpdate) -> Event:
        event = await self.get_by_id(event_id)
        update_data = event_in.model_dump(exclude_unset=True)

        if "total_seats" in update_data:
            seats_diff = update_data["total_seats"] - event.total_seats
            new_available = event.available_seats + seats_diff

            if new_available < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            event.available_seats = new_available

        for field, value in update_data.items():
            setattr(event, field, value)

        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def delete(self, event_id: int) -> None:
        event = self.get_by_id(event_id)
        await self.db.delete(event)
        await self.db.commit()