import pytest
from httpx import AsyncClient
from backend.app.main import app

# We use 'alice' as employee, 'carol' as manager for role variety

@pytest.mark.asyncio
async def test_employee_dashboard_shows_assigned_programs():
    # Login as alice
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/token", data={"username": "alice", "password": "secret"})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/dashboard/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_learners" in data
        assert "active_programs" in data

@pytest.mark.asyncio
async def test_manager_dashboard_shows_team_analytics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/token", data={"username": "carol", "password": "secret"})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/dashboard/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "team_analytics" in data
        assert "attendance" in data["team_analytics"]
