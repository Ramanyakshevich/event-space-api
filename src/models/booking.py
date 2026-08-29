from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.event import Event
    from src.models.user import User

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "cancelled"

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tickets_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[BookingStatus] = mapped_column(default=BookingStatus.PENDING, nullable=False)

    user: Mapped["User"] = relationship(back_populates="bookings")
    event: Mapped["Event"] = relationship(back_populates="bookings")