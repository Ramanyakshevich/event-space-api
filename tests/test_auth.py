import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "strongpassword123",
        "role": "USER",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    email = f"dup_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "strongpassword123",
        "role": "USER",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    email = f"login_{uuid.uuid4().hex[:6]}@example.com"
    user_data = {
        "email": email,
        "password": "password123",
        "role": "USER",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"