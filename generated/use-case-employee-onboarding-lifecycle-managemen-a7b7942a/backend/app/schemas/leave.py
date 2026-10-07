from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Optional

class LeaveType(str, Enum):
    sick = "Sick"
    casual = "Casual"
    earned = "Earned"
    unpaid = "Unpaid"

class LeaveStatus(str, Enum):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str

class LeaveUpdate(BaseModel):
    status: LeaveStatus
    manager_remarks: Optional[str] = None

class LeaveRead(BaseModel):
    leave_id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str
    status: LeaveStatus
    manager_remarks: Optional[str]

    class Config:
        orm_mode = True
