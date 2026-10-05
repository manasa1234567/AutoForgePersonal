from pydantic import BaseModel, EmailStr, constr
from datetime import date
from typing import Optional

class ApplicationBase(BaseModel):
    first_name: constr(min_length=1)
    last_name: constr(min_length=1)
    date_of_birth: date
    email: EmailStr
    phone: constr(min_length=7, max_length=25)
    address_line1: constr(min_length=1)
    address_line2: Optional[str] = None
    city: constr(min_length=1)
    state_province: constr(min_length=1)
    postal_code: constr(min_length=1)
    country: constr(min_length=1)
    signature: constr(min_length=3)  # typed full name

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int

    class Config:
        orm_mode = True
