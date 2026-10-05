from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
import pytest

client = TestClient(app)

# Setup and teardown for database tests
@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Application Form API is running."}


def test_submit_application_success():
    valid_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-01-01",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "address_line1": "123 Main St",
        "address_line2": "Apt 4",
        "city": "Anytown",
        "state_province": "CA",
        "postal_code": "12345",
        "country": "USA",
        "signature": "John Doe"
    }
    response = client.post("/submit", json=valid_data)
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp['first_name'] == valid_data['first_name']
    assert json_resp['email'] == valid_data['email']


def test_submit_application_missing_fields():
    invalid_data = {
        "first_name": "",
        "last_name": "",
        "date_of_birth": "",
        "email": "not-an-email",
        "phone": "",
        "address_line1": "",
        "city": "",
        "state_province": "",
        "postal_code": "",
        "country": "",
        "signature": ""
    }
    response = client.post("/submit", json=invalid_data)
    assert response.status_code == 422

