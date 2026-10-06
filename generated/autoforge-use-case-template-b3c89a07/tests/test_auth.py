import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_userinfo_unauthenticated():
    response = client.get("/api/auth/userinfo")
    assert response.status_code == 401

# Cannot fully test OAuth2 flow without real tokens

