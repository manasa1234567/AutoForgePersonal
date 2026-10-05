from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Application Form API")

# CORS for frontend React localhost port 3000 (adjust if deployed elsewhere)
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application form model
class EmploymentHistoryEntry(BaseModel):
    company_name: constr(strip_whitespace=True, min_length=1)
    position: constr(strip_whitespace=True, min_length=1)
    start_date: constr(regex=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    end_date: Optional[constr(regex=r"^\d{4}-\d{2}-\d{2}$")] = None  # optional if currently employed

class ApplicationForm(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone_number: constr(strip_whitespace=True, min_length=7, max_length=20)
    address: constr(strip_whitespace=True, min_length=1)
    city: constr(strip_whitespace=True, min_length=1)
    state: constr(strip_whitespace=True, min_length=1)
    postal_code: constr(strip_whitespace=True, min_length=1)
    country: constr(strip_whitespace=True, min_length=1)
    date_of_birth: constr(regex=r"^\d{4}-\d{2}-\d{2}$")
    education_level: constr(strip_whitespace=True, min_length=1)
    employment_history: List[EmploymentHistoryEntry]
    skills: List[constr(strip_whitespace=True, min_length=1)]
    additional_info: Optional[str] = None

# Temporary in-memory storage for submissions
submissions = []

@app.get("/")
async def root():
    return {"message": "Application Form API is running"}

@app.post("/submit")
async def submit_application(form: ApplicationForm):
    submissions.append(form)
    return {"message": "Application submitted successfully"}

@app.get("/submissions")
async def get_submissions():
    # Return all submissions as JSON
    return submissions
