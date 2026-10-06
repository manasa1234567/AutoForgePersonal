from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TrainingSessionBase(BaseModel):
    program_id: int
    title: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    capacity: int

class TrainingSessionCreate(TrainingSessionBase):
    pass

class TrainingSessionWithAttendance(TrainingSessionBase):
    id: int
    attendees_count: int
    class Config:
        orm_mode = True

class TrainingSession(TrainingSessionBase):
    id: int
    class Config:
        orm_mode = True
