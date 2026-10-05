import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root_status():
    response = client.get('/')
    assert response.status_code == 200
    assert 'message' in response.json()


def test_submit_application_missing_required():
    response = client.post('/submit-application', data={})
    assert response.status_code == 422


def test_submit_application_no_consent():
    data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'address': '123 Test Street',
        'city': 'Testville',
        'state': 'CA',
        'zip_code': '12345',
        'country': 'USA',
        'date_of_birth': '1990-01-01',
        'consent': False,
    }
    response = client.post('/submit-application', data=data)
    assert response.status_code == 400
    assert response.json()['detail'] == 'Consent required'


def test_submit_application_success():
    data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'address': '123 Test Street',
        'city': 'Testville',
        'state': 'CA',
        'zip_code': '12345',
        'country': 'USA',
        'date_of_birth': '1990-01-01',
        'consent': True,
    }
    response = client.post('/submit-application', data=data)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['detail'] == 'Application submitted successfully'
