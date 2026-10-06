import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Stub token for auth headers (in real cases, use a valid one or mock)
VALID_TOKEN = "Bearer validtoken"
INVALID_TOKEN = "Bearer invalidtoken"

headers = {"Authorization": VALID_TOKEN}

def test_read_current_user_unauthenticated():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

# This test relies on simplified stub always returning mock user
def test_read_current_user_authenticated():
    response = client.get("/api/v1/auth/me", headers={"Authorization": "validtoken"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "johndoe"


@pytest.mark.parametrize("role, expected_status", [
    ("Employee", 403),
    ("Administrator", 200)
])
def test_admin_access(role, expected_status):
    # Simulate token dependency returning user with role
    from fastapi import Depends
    from app.api.api_v1.endpoints.auth import verify_token, verify_admin, UserBase, UserRole
    from fastapi import APIRouter, HTTPException

    router = APIRouter()

    async def fake_verify_token():
        return UserBase(id=1, username="admin", email="admin@example.com", full_name="Admin User", role=UserRole.administrator if role=="Administrator" else UserRole.employee, is_active=True, date_joined=None)

    @router.get("/admin-only")
    async def admin_only(user=Depends(verify_admin)):
        return {"hello": "admin"}

    app.dependency_overrides[verify_token] = fake_verify_token
    app.include_router(router)

    response = client.get("/admin-only")
    assert response.status_code == expected_status
    if expected_status == 403:
        assert response.json()["detail"] in ["Access denied: administrator only", "Access denied"]

    # Cleanup
    app.dependency_overrides = {}
