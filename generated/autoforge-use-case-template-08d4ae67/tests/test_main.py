import pytest
from fastapi.testclient import TestClient
from app.main import app, users_db

client = TestClient(app)

# Override auth dependency for testing
from app.main import get_current_user
from app.main import UserBase, UserRole

def override_get_current_user_employee():
    # Return first employee user
    return UserBase(**users_db[0])

def override_get_current_user_trainer():
    # Return trainer
    return UserBase(**next(u for u in users_db if u["role"] == UserRole.trainer))

def override_get_current_user_manager():
    # Return manager
    return UserBase(**next(u for u in users_db if u["role"] == UserRole.manager))

def override_get_current_user_admin():
    # Return admin
    return UserBase(**next(u for u in users_db if u["role"] == UserRole.administrator))

from fastapi import Depends

app.dependency_overrides[get_current_user] = override_get_current_user_employee

def test_employee_dashboard():
    response = client.get("/dashboard/employee")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # AC001 check that assigned training programs appear
    program_ids = [prog["program_id"] for prog in data]
    assert 1 in program_ids


def test_submit_feedback_success():
    # AC002
    client.dependency_overrides[get_current_user] = override_get_current_user_employee
    response = client.post("/feedback", json={"session_id": 1, "rating": 4, "comments": "Good session."})
    assert response.status_code == 201
    assert response.json()["message"] == "Feedback submitted successfully."


def test_submit_feedback_invalid_rating():
    client.dependency_overrides[get_current_user] = override_get_current_user_employee
    response = client.post("/feedback", json={"session_id": 1, "rating": 6, "comments": "Bad rating."})
    assert response.status_code == 422


def test_mark_attendance_success():
    client.dependency_overrides[get_current_user] = override_get_current_user_trainer
    response = client.post("/sessions/1/attendance", params={"user_id": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Attendance recorded."


def test_mark_attendance_session_not_found():
    client.dependency_overrides[get_current_user] = override_get_current_user_trainer
    response = client.post("/sessions/999/attendance", params={"user_id": 1})
    assert response.status_code == 404


def test_manager_analytics():
    client.dependency_overrides[get_current_user] = override_get_current_user_manager
    response = client.get("/dashboard/manager/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "attendance_rate" in data
    assert "completion_rate" in data
    assert "feedback_trend" in data


def test_admin_access():
    client.dependency_overrides[get_current_user] = override_get_current_user_admin
    response = client.get("/admin/features")
    assert response.status_code == 200


def test_access_denied_for_non_admin():
    client.dependency_overrides[get_current_user] = override_get_current_user_employee
    response = client.get("/admin/features")
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

# Reset overrides after tests
@pytest.fixture(scope="module", autouse=True)
def reset_dep_overrides():
    yield
    app.dependency_overrides.clear()
