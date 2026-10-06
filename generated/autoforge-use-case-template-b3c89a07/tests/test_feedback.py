import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Override auth dependency
from app.services.auth import get_current_user
app.dependency_overrides[get_current_user] = lambda: type('User', (object,), {'id': '1'})()


def test_feedback_submit_success():
    payload = {
        "session_id": 1,
        "rating": 5,
        "comments": "Great session!"
    }
    response = client.post("/api/feedback/submit", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["message"] == "Feedback submitted successfully."


def test_feedback_submit_invalid_rating():
    payload = {
        "session_id": 1,
        "rating": 6,
        "comments": "Invalid rating test"
    }
    response = client.post("/api/feedback/submit", json=payload)
    assert response.status_code == 400
    assert "Rating must be between 1 and 5" in response.text
