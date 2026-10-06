from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional
from enum import Enum

class TrainingProgramRead(BaseModel):
    id: int
    title: constr(min_length=1, max_length=200)
    description: Optional[str]

    class Config:
        orm_mode = True

class TrainingSessionRead(BaseModel):
    id: int
    program_id: int
    title: constr(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    max_capacity: int

    class Config:
        orm_mode = True

class AttendanceRead(BaseModel):
    session_id: int
    user_id: int
    attended: bool

    class Config:
        orm_mode = True

class FeedbackCreate(BaseModel):
    rating: float
    comments: Optional[constr(max_length=1000)] = None

class FeedbackRead(BaseModel):
    id: int
    session_id: int
    user_id: int
    rating: float
    comments: Optional[str]

    class Config:
        orm_mode = True
