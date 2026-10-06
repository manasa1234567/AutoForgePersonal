import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/token", data={"username": "alice", "password": "secret"})
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/token", data={"username": "alice", "password": "wrong"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_login_unknown_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/token", data={"username": "unknown", "password": "secret"})
        assert response.status_code == 401
