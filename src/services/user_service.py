from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from watchfiles import awatch

from src.models.user import User, UserRole
from src.models.refresh_token import RefreshToken
from src.schemas.user import UserCreate, Token
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        user = select(User).where(User.email == email)
        result = await self.db.execute(user)
        return result.scalar_one_or_none()

    async def register(self, user_in: UserCreate) -> User:
        existing_user = await self.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        new_user = User(
            email=user_in.email,
            hashed_password = hash_password(user_in.password),
            role=UserRole.USER,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong email or password"
            )
        return user

    async def create_tokens_for_user(self, user: User) -> Token:
        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token_str = create_refresh_token(subject=user.id)

        payload = decode_jwt_token(refresh_token_str)
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        db_refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=expires_at
        )
        self.db.add(db_refresh_token)
        await self.db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str
        )

    async def refresh_tokens(self, refresh_token_str: str) -> Token:
        payload = decode_jwt_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh-token"
            )

        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str, RefreshToken.is_revoked == False)
        result = await self.db.execute(stmt)
        db_token = result.scalar_one_or_none()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalid or doesn't exists"
            )

        db_token.is_revoked = True
        await self.db.commit()

        stmt_user = select(User).where(User.id == int(payload["sub"]))
        res_user = await self.db.execute(stmt_user)
        user = res_user.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return await self.create_tokens_for_user(user)