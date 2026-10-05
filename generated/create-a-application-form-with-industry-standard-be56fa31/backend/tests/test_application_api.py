import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, timedelta

client = TestClient(app)

valid_payload = {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": (date.today() - timedelta(days=365 * 30)).isoformat(),
    "gender": "male",
    "email": "john.doe@example.com",
    "phone": "123-456-7890",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "State",
    "postal_code": "12345",
    "country": "United States",
    "highest_education": "Bachelor’s Degree",
    "experience_years": 5,
    "resume_consent": True,
    "terms_agree": True
}

invalid_payload_missing_required = valid_payload.copy()
invalid_payload_missing_required.pop('first_name')

invalid_payload_invalid_email = valid_payload.copy()
invalid_payload_invalid_email['email'] = 'invalid-email'

invalid_payload_dob_future = valid_payload.copy()
invalid_payload_dob_future['date_of_birth'] = (date.today() + timedelta(days=1)).isoformat()

invalid_payload_terms_disagree = valid_payload.copy()
invalid_payload_terms_disagree['terms_agree'] = False

@pytest.mark.parametrize('payload, status_code', [
    (valid_payload, 201),
    (invalid_payload_missing_required, 422),
    (invalid_payload_invalid_email, 422),
    (invalid_payload_dob_future, 422),
    (invalid_payload_terms_disagree, 422),
])
def test_submit_application(payload, status_code):
    response = client.post('/application/submit', json=payload)
    assert response.status_code == status_code
    if status_code == 201:
        assert response.json().get('message') == 'Application submitted successfully'
