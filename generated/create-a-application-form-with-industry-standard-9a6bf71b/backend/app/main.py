from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Application Form API")

# Read allowed origins from environment variable for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the application form data schema
class ApplicationForm(BaseModel):
    # Personal Information
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone: constr(strip_whitespace=True, min_length=7, max_length=15)

    # Address
    address_line1: constr(strip_whitespace=True, min_length=1)
    address_line2: constr(strip_whitespace=True) | None = None
    city: constr(strip_whitespace=True, min_length=1)
    state_province: constr(strip_whitespace=True, min_length=1)
    postal_code: constr(strip_whitespace=True, min_length=1)
    country: constr(strip_whitespace=True, min_length=1)

    # Additional Application Details
    date_of_birth: constr(strip_whitespace=True, min_length=10, max_length=10)  # YYYY-MM-DD format
    gender: constr(strip_whitespace=True, min_length=1)
    position_applied: constr(strip_whitespace=True, min_length=1)
    education_level: constr(strip_whitespace=True, min_length=1)
    years_of_experience: int

    # Consent
    accept_terms: bool

@app.get("/")
async def root():
    return {"message": "Application Form API is running."}

@app.post("/submit")
async def submit_application(form: ApplicationForm):
    # Validate accept_terms explicitly
    if not form.accept_terms:
        raise HTTPException(status_code=400, detail="Terms and conditions must be accepted.")

    # Here, normally integrate with database to persist data
    # For demo, just return success and echoed data (excluding sensitive)
    return {"status": "success", "submitted_data": form.dict(exclude={"accept_terms"})}


# Additional endpoint can be added if needed for dynamic lists, validations etc.
