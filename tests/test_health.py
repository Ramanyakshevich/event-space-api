from httpx import AsyncClient


async def test_health_check(client: AsyncClient):
    response = await client.get("/docs")
    assert response.status_code == 200