from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class UserRole(str, Enum):
    employee = "Employee"
    trainer = "Trainer/Mentor"
    manager = "Manager"
    administrator = "Administrator"
    coordinator = "Learning Program Coordinator"

class UserBase(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    date_joined: datetime | None

    class Config:
        from_attributes = True
