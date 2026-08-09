from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, description="Password must be at least 8 characters")

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str