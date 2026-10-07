from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import date

class EmployeeBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[constr(min_length=7, max_length=15)] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    manager: Optional[str] = None
    location: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeRead(EmployeeBase):
    employee_id: int
    is_active: bool

    class Config:
        orm_mode = True
