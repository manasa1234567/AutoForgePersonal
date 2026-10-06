import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

valid_headers = {"Authorization": "validtoken"}

@pytest.mark.asyncio
async def test_submit_feedback_valid(monkeypatch):
    # Override verify_token to simulate logged-in user
    class FakeUser:
        id = 1

    async def fake_verify_token():
        return FakeUser()

    app.dependency_overrides["app.api.deps.verify_token"] = fake_verify_token

    response = client.post("/api/v1/feedback/", json={"session_id": 101, "rating": 4, "comments": "Good training."}, headers={"Authorization": "validtoken"})
    assert response.status_code == 200
    assert response.json()["message"] == "Feedback saved successfully."

@pytest.mark.asyncio
async def test_submit_feedback_invalid_rating(monkeypatch):
    class FakeUser:
        id = 1

    async def fake_verify_token():
        return FakeUser()

    app.dependency_overrides["app.api.deps.verify_token"] = fake_verify_token

    response = client.post("/api/v1/feedback/", json={"session_id": 101, "rating": 6}, headers={"Authorization": "validtoken"})
    assert response.status_code == 400
    assert "Rating must be between 1 and 5" in response.json()["detail"]

@pytest.mark.asyncio
async def test_submit_feedback_invalid_session(monkeypatch):
    class FakeUser:
        id = 1

    async def fake_verify_token():
        return FakeUser()

    app.dependency_overrides["app.api.deps.verify_token"] = fake_verify_token

    response = client.post("/api/v1/feedback/", json={"session_id": 0, "rating": 4}, headers={"Authorization": "validtoken"})
    assert response.status_code == 400
    assert "Invalid session ID" in response.json()["detail"]

app.dependency_overrides = {}
