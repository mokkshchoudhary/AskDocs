import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    payload = {"email": "test@example.com", "password": "password123"}
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    payload = {"username": "test@example.com", "password": "password123"}
    response = await client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
