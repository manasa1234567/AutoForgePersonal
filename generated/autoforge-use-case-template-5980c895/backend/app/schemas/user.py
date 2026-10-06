from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    TRAINER = "Trainer"
    MANAGER = "Manager"
    ADMIN = "Administrator"

class UserRead(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    is_active: bool
    role: UserRole

    class Config:
        orm_mode = True
