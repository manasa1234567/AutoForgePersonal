import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_mark_attendance_within_capacity():
    # Login as trainer
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_resp = await client.post("/auth/token", data={"username": "bob", "password": "secret"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        attendance_data = {"session_id": 1, "employee_id": 1, "present": True}
        response = await client.post("/attendance/", json=attendance_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["present"] is True

@pytest.mark.asyncio
async def test_list_attendance_as_manager():
    # Login as manager
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_resp = await client.post("/auth/token", data={"username": "carol", "password": "secret"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/attendance/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
