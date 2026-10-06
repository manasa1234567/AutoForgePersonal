import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Fake user tokens for roles

class FakeUser:
    def __init__(self, role):
        from app.models.user import UserRole
        self.id = 1
        self.role = role

async def fake_verify_token_employee():
    from app.models.user import UserRole
    return FakeUser(UserRole.employee)

async def fake_verify_token_trainer():
    from app.models.user import UserRole
    return FakeUser(UserRole.trainer)

async def fake_verify_token_manager():
    from app.models.user import UserRole
    return FakeUser(UserRole.manager)

@pytest.mark.asyncio
async def test_list_sessions_employee(monkeypatch):
    monkeypatch.setattr("app.api.deps.verify_token", fake_verify_token_employee)
    response = client.get("/api/v1/sessions/", headers={"Authorization": "validtoken"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_register_session_success(monkeypatch):
    monkeypatch.setattr("app.api.deps.verify_token", fake_verify_token_employee)
    # register for session 101 (capacity not full)
    response = client.post("/api/v1/sessions/register/101", headers={"Authorization": "validtoken"})
    assert response.status_code == 200
    assert "message" in response.json()

@pytest.mark.asyncio
async def test_register_session_capacity_full(monkeypatch):
    monkeypatch.setattr("app.api.deps.verify_token", fake_verify_token_employee)
    # Session 102 has capacity full
    response = client.post("/api/v1/sessions/register/102", headers={"Authorization": "validtoken"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Session capacity reached"

@pytest.mark.asyncio
async def test_mark_attendance_permission(monkeypatch):
    monkeypatch.setattr("app.api.deps.verify_token", fake_verify_token_employee)
    response = client.post("/api/v1/sessions/attendance/101", headers={"Authorization": "validtoken"})
    # Employee lacks permission
    assert response.status_code == 403

    monkeypatch.setattr("app.api.deps.verify_token", fake_verify_token_trainer)
    response = client.post("/api/v1/sessions/attendance/101", headers={"Authorization": "validtoken"})
    assert response.status_code == 200
    assert "message" in response.json()

    monkeypatch.setattr("app.api.deps.verify_token", fake_verify_token_manager)
    response = client.post("/api/v1/sessions/attendance/101", headers={"Authorization": "validtoken"})
    assert response.status_code == 200

