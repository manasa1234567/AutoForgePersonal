import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

valid_headers = {"Authorization": "validtoken"}

@pytest.mark.parametrize("role", ["employee", "manager", "trainer"])
def test_get_dashboard(role):
    # Override the verify_token dependency to simulate roles
    from app.api.api_v1.endpoints.auth import UserBase, UserRole
    from app.api.api_v1.endpoints.dashboard import get_dashboard
    from fastapi import Depends

    async def fake_verify_token():
        return UserBase(id=1, username="user", email="user@example.com", full_name="User", role=UserRole(role), is_active=True, date_joined=None)

    app.dependency_overrides = {}
    app.dependency_overrides['app.api.api_v1.endpoints.dashboard.verify_token'] = fake_verify_token
    app.dependency_overrides['app.api.deps.verify_token'] = fake_verify_token

    response = client.get("/api/v1/dashboard/", headers={"Authorization": "validtoken"})
    assert response.status_code == 200
    data = response.json()

    if role == "employee":
        assert "total_learners" in data
        assert "active_programs" in data
        assert "completion_rate_percent" in data
    elif role == "manager":
        assert "team_learning_progress" in data
        assert "attendance_stats" in data
    else:
        assert "message" in data

    app.dependency_overrides = {}
