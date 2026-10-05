import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

valid_form_data = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "dateOfBirth": "1990-01-01",
    "gender": "male",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "Anystate",
    "postalCode": "12345",
    "country": "USA",
    "position": "Developer",
    "expectedSalary": "50000",
    "startDate": "2024-10-01",
    "coverLetter": "I am interested in this position.",
    "agreeToTerms": "true",
}


def test_root_endpoint():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Application Form Backend Running"}


def test_submit_application_success(tmp_path):
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"PDF content")

    with open(resume_path, "rb") as resume_file:
        files = {"resume": ("resume.pdf", resume_file, "application/pdf")}
        response = client.post("/api/applications", data=valid_form_data, files=files)

    assert response.status_code == 201
    assert response.json()["message"] == "Application received successfully."


def test_submit_application_missing_required_field(tmp_path):
    data = valid_form_data.copy()
    del data['firstName']
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"PDF content")

    with open(resume_path, "rb") as resume_file:
        files = {"resume": ("resume.pdf", resume_file, "application/pdf")}
        response = client.post("/api/applications", data=data, files=files)

    assert response.status_code == 422 or response.status_code == 400


def test_submit_application_no_agreement(tmp_path):
    data = valid_form_data.copy()
    data['agreeToTerms'] = "false"
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"PDF content")

    with open(resume_path, "rb") as resume_file:
        files = {"resume": ("resume.pdf", resume_file, "application/pdf")}
        response = client.post("/api/applications", data=data, files=files)

    assert response.status_code == 400
    assert "Terms must be agreed" in response.json().get("detail", "")


def test_submit_application_invalid_resume_type(tmp_path):
    data = valid_form_data.copy()
    invalid_resume_path = tmp_path / "resume.txt"
    invalid_resume_path.write_text("Not a valid file")

    with open(invalid_resume_path, "rb") as resume_file:
        files = {"resume": ("resume.txt", resume_file, "text/plain")}
        response = client.post("/api/applications", data=data, files=files)

    assert response.status_code == 400
    assert "Invalid resume file type" in response.json().get("detail", "")
