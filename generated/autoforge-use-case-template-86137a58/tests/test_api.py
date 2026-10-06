import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_employee():
    response = client.get("/dashboard", headers=auth_headers("employee-token"))
    assert response.status_code == 200
    data = response.json()
    assert "total_learners" in data
    assert data["total_learners"] == 2500


def test_assigned_programs_employee():
    response = client.get("/programs/assigned", headers=auth_headers("employee-token"))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["program_name"] == "Safety Training" for p in data)


def test_submit_feedback_success():
    feedback = {"session_id": "s1", "rating": 5, "comments": "Great session!"}
    response = client.post("/feedback", headers=auth_headers("employee-token"), json=feedback)
    assert response.status_code == 201
    assert response.json()["message"] == "Feedback submitted successfully"


def test_submit_feedback_missing_rating():
    feedback = {"session_id": "s1"}
    response = client.post("/feedback", headers=auth_headers("employee-token"), json=feedback)
    assert response.status_code == 422


def test_mark_attendance_trainer():
    attendance = {"session_id": "s1", "participant_id": "u1", "present": True}
    response = client.post("/attendance/mark", headers=auth_headers("trainer-token"), json=attendance)
    assert response.status_code == 200
    assert response.json()["message"] == "Attendance marked successfully"


def test_mark_attendance_forbidden():
    attendance = {"session_id": "s1", "participant_id": "u1", "present": True}
    response = client.post("/attendance/mark", headers=auth_headers("employee-token"), json=attendance)
    assert response.status_code == 403


def test_manager_team_analytics():
    response = client.get("/team/analytics", headers=auth_headers("manager-token"))
    assert response.status_code == 200
    data = response.json()
    assert "attendance_percentage" in data
    assert data["completion_rate"] > 0


def test_access_admin_features_denied_for_employee():
    response = client.get("/admin/users", headers=auth_headers("employee-token"))
    assert response.status_code == 403


def test_admin_list_users():
    response = client.get("/admin/users", headers=auth_headers("admin-token"))
    assert response.status_code == 200
    data = response.json()
    assert any(user["name"] == "Dave Admin" for user in data)


def test_admin_create_user():
    new_user = {"name": "Eve New", "email": "eve@example.com", "roles": ["Employee"]}
    response = client.post("/admin/users", headers=auth_headers("admin-token"), json=new_user)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Eve New"

