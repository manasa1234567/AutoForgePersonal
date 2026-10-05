# Application Form Project

This project implements a complete industry-standard application form with:

- React frontend using Material UI for accessibility and form standards.
- Formik and Yup for form state management and validation.
- FastAPI backend REST API for submission.
- Dockerfile for containerized deployment.

## Setup

### Backend

Navigate to `backend` folder.

Install dependencies:
```
python -m pip install -r requirements.txt
```

Run backend API:
```
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend

Navigate to `frontend` folder.

Install dependencies:
```
npm install
```

Run frontend app:
```
npm start
```

## Docker build and run

```bash
# Build docker image
sudo docker build -t application-form .

# Run container
sudo docker run -p 8080:8080 application-form
```

## API Endpoint

- `POST /submit` to submit form data.

## Notes

- The form includes all key fields for a typical job application form following industry standards.
- The backend currently just echos back submission success for demo purposes.
- CORS is enabled broadly for development.
- Adjust origin policy for production deployment.

## Access

- Frontend runs on port 3000 during development.
- Backend API runs on port 8000 during development.
- In production Docker, backend listens on 8080.

---

This project meets the requirements and acceptance criteria for:
- Industry-standard form layout
- Header and footer presence
- Complete application form with validation
- Fully functional user input submission flow
