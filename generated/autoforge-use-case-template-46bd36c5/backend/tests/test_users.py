import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_header_admin():
    return {"Authorization": "Bearer fake-supertoken-for-admin"}

@pytest.fixture
def auth_header_employee():
    return {"Authorization": "Bearer fake-supertoken-for-employee"}


def test_get_current_user_profile(auth_header_employee):
    response = client.get("/users/me", headers=auth_header_employee)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "employee"


def test_list_users_admin(auth_header_admin):
    response = client.get("/users/", headers=auth_header_admin)
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0


def test_list_users_non_admin(auth_header_employee):
    response = client.get("/users/", headers=auth_header_employee)
    assert response.status_code == 403


def test_create_user_admin(auth_header_admin):
    new_user = {
        "name": "New User",
        "email": "newuser@example.com",
        "role": "employee"
    }
    response = client.post("/users/", json=new_user, headers=auth_header_admin)
    assert response.status_code == 201
    assert response.json()["name"] == "New User"


def test_create_user_non_admin(auth_header_employee):
    new_user = {
        "name": "New User",
        "email": "newuser@example.com",
        "role": "employee"
    }
    response = client.post("/users/", json=new_user, headers=auth_header_employee)
    assert response.status_code == 403
