import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_get_assigned_programs_employee_token():
    headers = {"Authorization": "Bearer employee_token"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/employee/programs", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_submit_incomplete_feedback_shows_error():
    headers = {"Authorization": "Bearer employee_token"}
    incomplete_feedback = {"session_id": 1}  # missing rating
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/employee/feedback", json=incomplete_feedback, headers=headers)
    assert response.status_code == 400
    assert "incomplete" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_submit_complete_feedback_succeeds():
    headers = {"Authorization": "Bearer employee_token"}
    feedback = {"session_id": 1, "rating": 4, "comments": "Good session."}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/employee/feedback", json=feedback, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == 1
    assert data["rating"] == 4

@pytest.mark.asyncio
async def test_access_admin_without_admin_role_is_denied():
    headers = {"Authorization": "Bearer employee_token"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/admin/users", headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_access_root_path_returns_200():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Learning Management System API is running"
