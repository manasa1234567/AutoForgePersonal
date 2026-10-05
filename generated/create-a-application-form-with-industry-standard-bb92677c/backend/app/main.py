from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Application Form API")

# Allow CORS for frontend development. Adjust origins as needed in production.
origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Application Form API is running."}

# POST endpoint to receive application submissions
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from fastapi import HTTPException

class ApplicationForm(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)
    date_of_birth: constr(strip_whitespace=True, min_length=10, max_length=10)  # ISO Date yyyy-mm-dd
    email: EmailStr
    phone_number: constr(strip_whitespace=True, min_length=7, max_length=15)
    address_line1: constr(strip_whitespace=True, min_length=1)
    address_line2: Optional[str] = None
    city: constr(strip_whitespace=True, min_length=1)
    state_province: constr(strip_whitespace=True, min_length=1)
    postal_code: constr(strip_whitespace=True, min_length=3)
    country: constr(strip_whitespace=True, min_length=1)
    education_level: constr(strip_whitespace=True, min_length=1)
    position_applied_for: constr(strip_whitespace=True, min_length=1)
    cover_letter: Optional[str] = None

@app.post("/submit")
async def submit_application(application: ApplicationForm):
    # For demonstration, just return the submitted data with a success message
    # In a real app you would store this in a database
    return {"message": "Application received successfully.", "application": application.dict()}
