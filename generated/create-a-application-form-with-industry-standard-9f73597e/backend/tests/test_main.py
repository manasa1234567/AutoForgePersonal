from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

valid_payload = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "date_of_birth": "1990-01-01",
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "Anytown",
    "state_province": "State",
    "postal_code": "12345",
    "country": "United States",
    "education_level": "Bachelor’s Degree",
    "employment_status": "Full-time",
    "resume_text": "Experienced professional.",
    "agree_to_terms": True
}

invalid_payload_no_terms = valid_payload.copy()
invalid_payload_no_terms["agree_to_terms"] = False

invalid_payload_missing_required = valid_payload.copy()
del invalid_payload_missing_required["first_name"]


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_submit_valid():
    response = client.post("/submit", json=valid_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["message"] == "Application submitted successfully."
    assert "id" in json_data


def test_submit_no_terms():
    response = client.post("/submit", json=invalid_payload_no_terms)
    assert response.status_code == 400
    assert response.json()["detail"] == "Terms agreement is required."


def test_submit_missing_required():
    response = client.post("/submit", json=invalid_payload_missing_required)
    assert response.status_code == 422
