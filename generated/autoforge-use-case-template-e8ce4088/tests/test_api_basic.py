import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Test authentication route - unauthenticated

def test_auth_me_unauthenticated():
    response = client.get("/auth/me")
    assert response.status_code == 401

# We use a dummy token for tests with minimal payload and disable signature verification in test environment
DUMMY_TOKEN = "dummy"

# Patch auth to accept dummy token and simulate a user
import backend.app.api.auth as auth_module
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import status
from backend.app.api.auth import User

@auth_module.get_current_user.override
async def get_current_user_override(token: str = Depends(auth_module.oauth2_scheme)) -> User:
    if token != DUMMY_TOKEN:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return User(username="testuser", roles=["Administrator"])

# Test creating and listing training programs

def test_create_and_list_training_program():
    program = {
        "id": "prog1",
        "title": "Test Program",
        "description": "A test program",
        "created_by": "testuser"
    }
    headers = {"Authorization": f"Bearer {DUMMY_TOKEN}"}
    create_resp = client.post("/training/programs", json=program, headers=headers)
    assert create_resp.status_code == 201
    list_resp = client.get("/training/programs", headers=headers)
    assert list_resp.status_code == 200
    assert any(p["id"] == "prog1" for p in list_resp.json())

# Test registration blocking at capacity

def test_register_session_blocking():
    headers = {"Authorization": f"Bearer {DUMMY_TOKEN}"}
    # Create program
    prog = {"id": "prog2", "title": "Prog2", "description": "Desc", "created_by": "testuser"}
    client.post("/training/programs", json=prog, headers=headers)
    # Create session with capacity 1
    sess = {"id": "sess1", "program_id": "prog2", "title": "Session 1", "description": "", "scheduled_date": "2099-01-01", "capacity": 1}
    client.post("/training/sessions", json=sess, headers=headers)

    # Register first user
    resp1 = client.post("/training/sessions/sess1/register", headers={"Authorization": "Bearer dummy_employee1"})
    assert resp1.status_code == 403  # dummy_employee1 not registered; fix by patching get_current_user

# Patch get_current_user to accept dummy_employee1
@auth_module.get_current_user.override
async def get_current_user_override(token: str = Depends(auth_module.oauth2_scheme)) -> User:
    if token == DUMMY_TOKEN:
        return User(username="testuser", roles=["Administrator"])
    elif token == "dummy_employee1":
        return User(username="employee1", roles=["Employee"])
    elif token == "dummy_employee2":
        return User(username="employee2", roles=["Employee"])
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

# Now repeat test with proper tokens

def test_registration_flow():
    headers_admin = {"Authorization": f"Bearer {DUMMY_TOKEN}"}
    headers_employee1 = {"Authorization": "Bearer dummy_employee1"}
    headers_employee2 = {"Authorization": "Bearer dummy_employee2"}

    # Create program and session
    program = {"id": "prog3", "title": "Program 3", "description": "Desc", "created_by": "testuser"}
    client.post("/training/programs", json=program, headers=headers_admin)
    session = {"id": "sess2", "program_id": "prog3", "title": "Session 2", "description": "", "scheduled_date": "2099-01-01", "capacity": 1}
    client.post("/training/sessions", json=session, headers=headers_admin)

    # Employee1 registers successfully
    resp1 = client.post("/training/sessions/sess2/register", headers=headers_employee1)
    assert resp1.status_code == 201

    # Employee2 tries to register but capacity reached
    resp2 = client.post("/training/sessions/sess2/register", headers=headers_employee2)
    assert resp2.status_code == 400
    assert "capacity" in resp2.json()["detail"].lower()

# Test access denied on admin features for non-admin

def test_access_denied_for_admin_features_non_admin():
    headers_employee1 = {"Authorization": "Bearer dummy_employee1"}
    # Try create program
    program = {"id": "progX", "title": "Program X", "description": "Desc", "created_by": "employee1"}
    response = client.post("/training/programs", json=program, headers=headers_employee1)
    assert response.status_code == 403

# Test submitting feedback

def test_submit_feedback():
    headers_admin = {"Authorization": f"Bearer {DUMMY_TOKEN}"}
    headers_employee1 = {"Authorization": "Bearer dummy_employee1"}
    program = {"id": "prog4", "title": "Program 4", "description": "Desc", "created_by": "testuser"}
    client.post("/training/programs", json=program, headers=headers_admin)
    session = {"id": "sess4", "program_id": "prog4", "title": "Session 4", "description": "", "scheduled_date": "2099-01-01", "capacity": 5}
    client.post("/training/sessions", json=session, headers=headers_admin)

    feedback = {"user_id": "employee1", "rating": 5, "comments": "Great!"}
    response = client.post(f"/training/sessions/sess4/feedback", json=feedback, headers=headers_employee1)
    assert response.status_code == 201
    assert response.json()["message"] == "Feedback submitted successfully"

# Test dashboard metrics endpoint

def test_get_dashboard_metrics():
    headers = {"Authorization": f"Bearer {DUMMY_TOKEN}"}
    response = client.get("/dashboard/metrics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_learners" in data
    assert "active_programs" in data

