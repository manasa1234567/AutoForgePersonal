import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

valid_payload = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "dateOfBirth": "1990-01-01",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "State",
    "zipCode": "12345",
    "country": "United States",
    "gender": "male",
    "educationLevel": "Bachelor Degree",
    "resumeText": "Experienced developer.",
    "agreeTerms": True
}

invalid_payload = {
    "firstName": "",
    "lastName": "",
    "email": "not-an-email",
    "phone": "123",
    "dateOfBirth": "",
    "address": "",
    "city": "",
    "state": "",
    "zipCode": "",
    "country": "",
    "gender": "",
    "educationLevel": "",
    "resumeText": "",
    "agreeTerms": False
}


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json().get('message') == 'Application Form API is running.'


def test_submit_valid_application():
    response = client.post('/api/applications', json=valid_payload)
    assert response.status_code == 201
    assert response.json().get('message') == 'Application submitted successfully'


def test_submit_invalid_application():
    response = client.post('/api/applications', json=invalid_payload)
    assert response.status_code == 422


def test_submit_without_agree_terms():
    data = valid_payload.copy()
    data['agreeTerms'] = False
    response = client.post('/api/applications', json=data)
    assert response.status_code == 400
    assert response.json().get('detail') == 'You must agree to the terms and conditions.'
