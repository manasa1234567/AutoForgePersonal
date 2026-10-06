import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Override auth for admin role test
from app.services.auth import get_current_user
from app.services.auth import require_role

# Create dummy admin user
class DummyAdmin:
    id = "4"
    username = "admin@company.com"
    roles = ["administrator"]

class DummyNonAdmin:
    id = "1"
    username = "user@company.com"
    roles = ["employee"]


def test_list_users_as_admin():
    app.dependency_overrides[get_current_user] = lambda: DummyAdmin()
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_as_nonadmin():
    app.dependency_overrides[get_current_user] = lambda: DummyNonAdmin()
    response = client.get("/api/users/")
    assert response.status_code == 403

