from pydantic import BaseModel
from enum import Enum
from typing import Optional

class TaskStatus(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"

class OnboardingTaskBase(BaseModel):
    employee_id: int
    task_name: str
    assigned_to: str
    status: TaskStatus
    remarks: Optional[str] = None

class OnboardingTaskRead(OnboardingTaskBase):
    task_id: int

    class Config:
        orm_mode = True

class OnboardingTaskUpdate(BaseModel):
    status: TaskStatus
    remarks: Optional[str] = None
