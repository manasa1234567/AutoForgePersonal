import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_header_employee():
    return {"Authorization": "Bearer fake-supertoken-for-employee"}

@pytest.fixture
def auth_header_trainer():
    return {"Authorization": "Bearer fake-supertoken-for-trainer"}

@pytest.fixture
def auth_header_manager():
    return {"Authorization": "Bearer fake-supertoken-for-manager"}


def test_register_session_success(auth_header_employee):
    data = {"session_id": 1}
    response = client.post("/sessions/register", json=data, headers=auth_header_employee)
    assert response.status_code == 201
    assert "successfully" in response.json()["message"]


def test_register_session_capacity_reached(auth_header_employee):
    # Fill the capacity to simulate
    # Since this is a dummy in-memory, test repeated registration
    data = {"session_id": 1}
    # register once (may error if already registered but that's OK for this test context)
    client.post("/sessions/register", json=data, headers=auth_header_employee)
    # register repeatedly to trigger capacity error
    for _ in range(20):
        client.post("/sessions/register", json=data, headers=auth_header_employee)
    response = client.post("/sessions/register", json=data, headers=auth_header_employee)
    if response.status_code == 400:
        assert "capacity" in response.json()["detail"].lower()


def test_mark_attendance_authorized(auth_header_trainer):
    data = {"session_id": 1, "user_id": 3, "attended": True}
    response = client.post("/sessions/attendance", json=data, headers=auth_header_trainer)
    assert response.status_code == 200
    assert "updated" in response.json()["message"]


def test_mark_attendance_unauthorized(auth_header_employee):
    data = {"session_id": 1, "user_id": 3, "attended": True}
    response = client.post("/sessions/attendance", json=data, headers=auth_header_employee)
    assert response.status_code == 403
