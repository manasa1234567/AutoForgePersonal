from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Application Form API is running."}

def test_create_application_success():
    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "dateOfBirth": "1985-01-01",
        "streetAddress": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postalCode": "90210",
        "country": "USA",
        "positionApplied": "Software Engineer",
        "resumeLink": "http://example.com/resume.pdf",
        "acceptTerms": True
    }

    response = client.post("/api/applications", json=payload)
    assert response.status_code == 201
    json_resp = response.json()
    assert "message" in json_resp
    assert json_resp["message"] == "Application submitted successfully"

def test_create_application_missing_required():
    payload = {
        "firstName": "",
        "lastName": "",
        "email": "invalid-email",
        "phone": "123",
        "dateOfBirth": "01-01-1985",
        "streetAddress": "",
        "city": "",
        "state": "",
        "postalCode": "",
        "country": "",
        "positionApplied": "",
        "acceptTerms": False
    }

    response = client.post("/api/applications", json=payload)
    assert response.status_code == 422
