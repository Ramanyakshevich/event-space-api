from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimestampMixin
if TYPE_CHECKING:
    from src.models.booking import Booking


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER, nullable=False)

    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )