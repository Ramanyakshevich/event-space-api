from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, status

from src.api.dependencies import EventServiceDep, CurrentAdminDep
from src.schemas.event import EventRead, EventCreate, EventUpdate, PaginatedResponse

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("", response_model=PaginatedResponse[EventRead])
async def get_events(
        event_service: EventServiceDep,
        page: int = Query(1, ge=1, description="Number of page"),
        size: int = Query(20, ge=1, le=100, description="Number of elements on page"),
        search: Optional[str] = Query(None, description="Name of event/location search"),
        date_from: Optional[datetime] = Query(None, description="Date from"),
        date_to: Optional[datetime] = Query(None, description="Date to"),
        only_available: bool = Query(False, description="Show only with available seats")
):
    return await event_service.get_list(
        page=page,
        size=size,
        search=search,
        date_from=date_from,
        date_to=date_to,
        only_available=only_available
    )

@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: int, event_service: EventServiceDep):
    return await event_service.get_by_id(event_id)

@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
        event_in: EventCreate,
        event_service: EventServiceDep,
        _: CurrentAdminDep
):
    return await event_service.create(event_in)

@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
        event_id: int,
        event_in: EventUpdate,
        event_service: EventServiceDep,
        _: CurrentAdminDep,
):
    return await event_service.update(event_id=event_id, event_in=event_in)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
        event_id: int,
        event_service: EventServiceDep,
        _: CurrentAdminDep
):
    await event_service.delete(event_id)


