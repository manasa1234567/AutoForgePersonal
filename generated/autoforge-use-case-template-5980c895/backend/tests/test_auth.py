import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", data={"username": "employee1", "password": "password1"})
        assert response.status_code == 200
        json_resp = response.json()
        assert "access_token" in json_resp
        assert json_resp["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_fail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", data={"username": "nonexistent", "password": "wrong"})
        assert response.status_code == 401
