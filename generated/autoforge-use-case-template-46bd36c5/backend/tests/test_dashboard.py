import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_header_employee():
    return {"Authorization": "Bearer fake-supertoken-for-employee"}

@pytest.fixture
def auth_header_manager():
    return {"Authorization": "Bearer fake-supertoken-for-manager"}

@pytest.fixture
def auth_header_admin():
    return {"Authorization": "Bearer fake-supertoken-for-admin"}

@pytest.mark.parametrize("token_fixture", ["auth_header_employee", "auth_header_manager", "auth_header_admin"])
def test_get_dashboard_widgets(token_fixture, request):
    headers = request.getfixturevalue(token_fixture)
    response = client.get("/dashboard/widgets", headers=headers)
    assert response.status_code == 200
    json_resp = response.json()
    assert "total_learners" in json_resp
    assert "active_programs" in json_resp
    assert isinstance(json_resp["total_learners"], int)


def test_get_assigned_sessions_employee(auth_header_employee):
    response = client.get("/dashboard/sessions/assigned", headers=auth_header_employee)
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)


def test_get_assigned_sessions_non_employee(auth_header_manager):
    response = client.get("/dashboard/sessions/assigned", headers=auth_header_manager)
    assert response.status_code == 403
