import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_bookings_empty(client: AsyncClient, user_token_headers: dict[str, str]):
    response = await client.get("/api/v1/bookings/my", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    if isinstance(data, dict) and "items" in data:
        assert len(data["items"]) == 0
    else:
        assert len(data) == 0

@pytest.mark.asyncio
async def test_create_booking_event_not_found(client: AsyncClient, user_token_headers: dict[str, str]):
    payload = {
        "event_id": 99999,
        "tickets_count": 2
    }
    response = await client.post(
        "api/v1/bookings",
        json=payload,
        headers=user_token_headers
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_unauthorized_booking_attempt(client: AsyncClient):
    payload = {
        "event": 1,
        "tickets_count": 1
    }
    response = await client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 401