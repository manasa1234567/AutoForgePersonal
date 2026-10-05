from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr, conint, validator
from typing import Optional
from datetime import date

router = APIRouter()

class ApplicationData(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1, max_length=50)
    last_name: constr(strip_whitespace=True, min_length=1, max_length=50)
    date_of_birth: date
    gender: constr(regex=r'^(male|female|other|preferNotToSay)$') if hasattr(constr, 'regex') else constr(min_length=1, max_length=20)
    email: EmailStr
    phone: constr(strip_whitespace=True, min_length=7, max_length=20)
    address: constr(strip_whitespace=True, min_length=1, max_length=100)
    city: constr(strip_whitespace=True, min_length=1, max_length=50)
    state: constr(strip_whitespace=True, min_length=1, max_length=50)
    postal_code: constr(strip_whitespace=True, min_length=3, max_length=10)
    country: constr(strip_whitespace=True, min_length=1, max_length=50)
    highest_education: constr(strip_whitespace=True, min_length=1, max_length=30)
    experience_years: conint(ge=0, le=80)
    resume_consent: Optional[bool] = False
    terms_agree: bool

    @validator('date_of_birth')
    def valid_dob(cls, v: date):
        from datetime import date as dt_date
        if v >= dt_date.today():
            raise ValueError('Date of birth must be in the past')
        return v

    @validator('postal_code')
    def postal_code_valid(cls, v: str):
        import re
        if not re.match(r'^[a-zA-Z0-9 \-]{3,10}$', v):
            raise ValueError('Invalid postal code format')
        return v

@router.post("/submit", status_code=201)
def submit_application(data: ApplicationData):
    # For now we simulate saving data and return success
    # Placeholder for DB or further processing
    return {"message": "Application submitted successfully"}
