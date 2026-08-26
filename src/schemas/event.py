from datetime import datetime
from typing import Optional, TypeVar, Generic, List

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Event name",
        examples=["Python Meetup Warsaw"]
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Event description",
        examples=["Async Python and FastAPI course"]
    )
    location: str = Field(
        ...,
        description="Venue of the event"
    )
    event_date: datetime = Field(
        ...,
        description="Date and time of the event"
    )
    price: int = Field(
        ...,
        gt=0,
        description="Ticket price in cents",
        examples=[1500]
    )
    total_seats: int = Field(
        ...,
        gt=0,
        description="Number of seats",
        examples=[100]
    )


class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    event_date: Optional[datetime] = None
    price: Optional[int] = Field(None, ge=0)
    total_seats: Optional[int] = Field(None, gt=0)

class EventRead(EventBase):
    id: int
    available_seats: int
    created_at: datetime
    updated_at: datetime

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}