from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr, conint
from typing import Optional

app = FastAPI(title="Application Form API")

class ApplicationForm(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone: constr(strip_whitespace=True, min_length=7, max_length=15)
    age: conint(ge=18, le=100)
    address: constr(strip_whitespace=True, min_length=10)
    city: constr(strip_whitespace=True, min_length=2)
    state: constr(strip_whitespace=True, min_length=2)
    postal_code: constr(strip_whitespace=True, min_length=4, max_length=10)
    country: constr(strip_whitespace=True, min_length=2)
    education_level: constr(strip_whitespace=True, min_length=2)
    experience_years: conint(ge=0, le=50)
    position_applied: constr(strip_whitespace=True, min_length=2)
    cover_letter: Optional[constr(strip_whitespace=True, max_length=2000)] = ""

@app.get("/", tags=["health"])
async def root():
    return {"status": "ok"}

@app.post("/submit", status_code=201, tags=["form"])
async def submit_application(application: ApplicationForm):
    # For demonstration, we just acknowledge submission.
    # In real scenarios, insert into DB or trigger workflows.
    # Validate fields through Pydantic model automatically.
    return {"message": "Application submitted successfully", "applicant": application.first_name + " " + application.last_name}
