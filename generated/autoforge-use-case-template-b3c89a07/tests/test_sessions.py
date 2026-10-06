import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Auth override
from app.services.auth import get_current_user
app.dependency_overrides[get_current_user] = lambda: type('User', (object,), {'id': '1'})()


def test_list_sessions():
    response = client.get("/api/sessions/")
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)


def test_register_session_success():
    payload = {"session_id": 1}
    response = client.post("/api/sessions/register", json=payload)
    assert response.status_code == 201
    assert "Successfully registered" in response.json().get("message", "")


def test_register_session_capacity_reached():
    # session_id=2 is full in stub data
    payload = {"session_id": 2}
    response = client.post("/api/sessions/register", json=payload)
    assert response.status_code == 400
    assert "capacity reached" in response.json()["detail"].lower()
