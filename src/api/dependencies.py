from typing import AsyncGenerator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.core.redis import get_redis
from src.core.security import decode_jwt_token
from src.models import UserRole
from src.models.user import User
from src.services.event_service import EventService
from src.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
RedisDep = Annotated[Redis, Depends(get_redis)]

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

DataBaseDep = Annotated[AsyncSessionLocal(), Depends(get_db)]

async def get_user_service(db: DataBaseDep) -> UserService:
    return UserService(db)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DataBaseDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Validation error",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_jwt_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

async def get_event_service(db: DataBaseDep, redis:RedisDep) -> EventService:
    return EventService(db, redis=redis)

EventServiceDep = Annotated[EventService, Depends(get_event_service)]

async def get_current_admin(current_user: CurrentUserDep) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator rights are required"
        )
    return current_user

CurrentAdminDep = Annotated[User, Depends(get_current_admin)]

