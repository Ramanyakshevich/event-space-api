from datetime import datetime
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from src.models import Base, TimestampMixin
if TYPE_CHECKING:
    from src.models.booking import Booking


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    event_date: Mapped[datetime] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)

    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )