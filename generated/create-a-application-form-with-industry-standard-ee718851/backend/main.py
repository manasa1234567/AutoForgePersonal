from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI(title="Application Form Backend API")

# Enable CORS for frontend (localhost and deployed)
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for application input
class ApplicationForm(BaseModel):
    firstName: constr(strip_whitespace=True, min_length=1)
    lastName: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone: constr(strip_whitespace=True, min_length=7)
    dateOfBirth: constr(strip_whitespace=True, min_length=1)  # ISO date string
    streetAddress: constr(strip_whitespace=True, min_length=1)
    city: constr(strip_whitespace=True, min_length=1)
    state: constr(strip_whitespace=True, min_length=1)
    postalCode: constr(strip_whitespace=True, min_length=1)
    country: constr(strip_whitespace=True, min_length=1)
    positionApplied: constr(strip_whitespace=True, min_length=1)
    resumeLink: Optional[str] = None
    acceptTerms: bool

    @validator('phone')
    def valid_phone(cls, v):
        # Simple regex for phone number validation
        if not re.match(r'^\+?[0-9\-()\s]{7,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

    @validator('dateOfBirth')
    def valid_date(cls, v):
        # Simple ISO format date check
        # YYYY-MM-DD
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Date of birth must be in YYYY-MM-DD format')
        return v

    @validator('acceptTerms')
    def must_accept_terms(cls, v):
        if v is not True:
            raise ValueError('Terms must be accepted')
        return v

# In-memory 'database' substitute
stored_applications = []

@app.get("/")
async def root():
    return {"message": "Application Form API is running."}

@app.post("/api/applications", status_code=201)
async def create_application(application: ApplicationForm):
    # Here would go DB insert logic
    # For now we just append to in-memory list
    stored_applications.append(application.dict())
    return {"message": "Application submitted successfully"}
