from datetime import timezone, datetime, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_event_forbidden_for_user(client: AsyncClient, user_token_headers: dict[str, str]):
    event_payload = {
        "title": "Hacker Meeting",
        "description": "Unauthorized attempt",
        "location": "Dark Alley",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "total_seats": 20,
        "available_seats": 20,
        "price": 500,
    }
    response = await client.post(
        "/api/v1/events",
        json=event_payload,
        headers=user_token_headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_events_list(client: AsyncClient, admin_token_headers: dict[str, str]):
    event_payload = {
        "title": "Public Meetup",
        "description": "Open for all",
        "location": "Hub Central",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=6)).isoformat(),
        "total_seats": 50,
        "available_seats": 50,
        "price": 0,
    }
    await client.post(
        "/api/v1/events",
        json=event_payload,
        headers=admin_token_headers
    )
    response = await client.get("/api/v1/events?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) >= 1

@pytest.mark.asyncio
async def test_single_event_not_found(client:AsyncClient):
    response = await client.get("/api/v1/events/99999")
    assert response.status_code == 404
