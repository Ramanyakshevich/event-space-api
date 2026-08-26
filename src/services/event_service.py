import math
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event
from src.schemas.event import EventCreate, EventUpdate


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
            self,
            page: int = 1,
            size: int = 20,
            search: Optional[str] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            only_available: bool = False
    ) -> Dict[str, Any]:
        query = select(Event)
        count_query = select(func.count()).select_from(Event)

        filters = []

        if search:
            search_filter = (
                Event.title.ilike(f"%{search}%") | Event.location.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        if date_from:
            filters.append(Event.event_date >= date_from)
        if date_to:
            filters.append(Event.event_date <= date_to)
        if only_available:
            filters.append(Event.available_seats > 0)
        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        query = query.order_by(Event.event_date.asc()).offset(offset).limit(size)

        result = await self.db.execute(query)
        items = result.scalars().all()

        pages = math.ceil(total / size) if total > 0 else 1

        return {
            "items": items,
            "total": total,
            "page" : page,
            "size": size,
            "pages": pages
        }

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
        self.db.add(new_event)

        await self.db.flush()
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
        event = await self.get_by_id(event_id)
        await self.db.delete(event)
        await self.db.commit()