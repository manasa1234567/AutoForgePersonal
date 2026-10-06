import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_access_denied_for_non_admin_on_admin_route():
    # Login as employee (not admin)
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_resp = await client.post("/auth/token", data={"username": "alice", "password": "secret"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/admin/", headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_access_allowed_for_admin_on_admin_route():
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_resp = await client.post("/auth/token", data={"username": "admin", "password": "secret"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/admin/", headers=headers)
        assert response.status_code == 200
        assert "Admin dashboard" in response.text
