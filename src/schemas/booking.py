from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field, ConfigDict

from src.schemas.event import EventRead


class BookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED ="confirmed"
    CANCELLED = "cancelled"

class BookingBase(BaseModel):
    event_id: int = Field(
        ...,
        gt=0,
        description="Event ID",
        examples=[1]
    )
    seats_count: int = Field(
        ...,
        gt=0,
        description="Number of booking seats (minimum 1)",
        examples=[2]
    )

class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    user_id: int
    status: BookingStatus
    total_price: int = Field(
        ...,
        description="Booking price",
        examples=[500]
    )
    created_at: datetime
    updated_at: datetime
    event: EventRead | None = None

    model_config = ConfigDict(from_attributes=True)
