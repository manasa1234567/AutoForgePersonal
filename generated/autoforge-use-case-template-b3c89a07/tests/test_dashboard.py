import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Using dependency override to mock get_current_user from auth
from app.api.dashboard import router as dashboard_router
from app.services.auth import get_current_user
from app.models.auth import User

class DummyUser:
    id = "1"
    username = "dummy"
    roles = ["employee"]

app.dependency_overrides[get_current_user] = lambda: DummyUser()

def test_get_dashboard():
    response = client.get("/api/dashboard/")
    assert response.status_code == 200
    json_data = response.json()
    assert "total_learners" in json_data
    assert "active_programs" in json_data

