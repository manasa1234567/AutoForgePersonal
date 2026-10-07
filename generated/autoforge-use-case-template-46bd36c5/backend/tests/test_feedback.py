import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_header_employee():
    return {"Authorization": "Bearer fake-supertoken-for-employee"}

@pytest.fixture
def auth_header_admin():
    return {"Authorization": "Bearer fake-supertoken-for-admin"}


def test_submit_feedback_success(auth_header_employee):
    data = {"session_id": 1, "rating": 5, "comments": "Great session"}
    response = client.post("/feedback/submit", json=data, headers=auth_header_employee)
    assert response.status_code == 201
    assert response.json()["message"] == "Feedback submitted successfully"


def test_submit_feedback_missing_fields(auth_header_employee):
    data = {"session_id": 1}  # missing rating
    response = client.post("/feedback/submit", json=data, headers=auth_header_employee)
    assert response.status_code == 422  # validation error from Pydantic


def test_submit_feedback_invalid_rating(auth_header_employee):
    data = {"session_id": 1, "rating": 6}
    response = client.post("/feedback/submit", json=data, headers=auth_header_employee)
    assert response.status_code == 400
    assert "Rating" in response.json()["detail"]
