import uuid
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.core.config import settings
from src.core.database import get_db
import src.core.redis as app_redis
from src.main import app
from src.models.base import Base

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/eventspace_db", "/eventspace_test_db")

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def init_redis():
    test_redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/9"
    client = aioredis.from_url(test_redis_url, decode_responses=False)
    app_redis.redis_client = client
    yield client
    await client.flushdb()
    await client.aclose()
    app_redis.redis_client = None


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_token_headers(client: AsyncClient) -> dict[str, str]:
    email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
    admin_data = {"email": email, "password": "adminpassword123"}
    await client.post("/api/v1/auth/register", json=admin_data)
    async with test_engine.begin() as conn:
        await conn.execute(
            text("UPDATE users SET role = 'ADMIN' WHERE email = :email"),
            {"email": email}
        )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": admin_data["email"], "password": admin_data["password"]},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def user_token_headers(client: AsyncClient) -> dict[str, str]:
    email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    user_data = {"email": email, "password": "userpassword123", "role": "USER"}
    await client.post("/api/v1/auth/register", json=user_data)
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}