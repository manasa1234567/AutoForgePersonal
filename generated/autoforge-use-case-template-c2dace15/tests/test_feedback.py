import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_feedback_submission_and_listing():
    # Login as employee
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/token", data={"username": "alice", "password": "secret"})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Submit feedback - valid
        feedback_data = {"session_id": 1, "employee_id": 1, "rating": 5, "comments": "Great session!"}
        response = await client.post("/feedback/", json=feedback_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5
        assert data["comments"] == "Great session!"

@pytest.mark.asyncio
async def test_feedback_submission_validation():
    # Login as employee
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/token", data={"username": "alice", "password": "secret"})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Submit feedback with missing rating
        feedback_data = {"session_id": 1, "employee_id": 1, "comments": "Missing rating"}
        response = await client.post("/feedback/", json=feedback_data, headers=headers)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_feedback_listing_by_trainer():
    # Login as trainer
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post("/auth/token", data={"username": "bob", "password": "secret"})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/feedback/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
