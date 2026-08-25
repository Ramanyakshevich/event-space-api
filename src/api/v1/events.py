from typing import List
from fastapi import APIRouter, Query, status

from src.api.dependencies import EventServiceDep, CurrentAdminDep
from src.schemas.event import EventRead, EventCreate, EventUpdate

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("", response_model=List[EventRead])
async def get_events(
        event_service: EventServiceDep,
        skip: int = Query(0, ge=1, description="Number of skipped records "),
        limit: int = Query(20, ge=1, le=100, description="Returned records limit")
):
    return await event_service.get_list(skip=skip, limit=limit)

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


