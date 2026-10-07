from pydantic import BaseModel, constr, Field
from typing import List, Optional
from datetime import date, datetime

# User schemas
class UserBase(BaseModel):
    username: constr(min_length=1)
    role: constr(min_length=1)

class UserCreate(UserBase):
    pass

class User(UserBase):
    full_name: Optional[str]
    email: Optional[constr(min_length=1)]

# Training Program
class TrainingProgramBase(BaseModel):
    id: constr(min_length=1)
    title: str
    description: Optional[str]
    created_by: str

class TrainingProgramCreate(TrainingProgramBase):
    pass

class TrainingProgram(TrainingProgramBase):
    pass

# Session
class SessionBase(BaseModel):
    id: constr(min_length=1)
    program_id: constr(min_length=1)
    title: str
    description: Optional[str]
    scheduled_date: date
    capacity: int = Field(..., ge=1)

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    pass

# Attendance
class AttendanceRecord(BaseModel):
    user_id: constr(min_length=1)
    present: bool

# Feedback
class FeedbackSubmit(BaseModel):
    user_id: constr(min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str]

# Dashboard Metrics
class DashboardMetrics(BaseModel):
    total_learners: int
    active_programs: int
    completion_rate: float
    upcoming_sessions: int
    attendance_trend: List[int]
    feedback_rating: List[int]
    recent_activities: List[str]
    top_performing_learners: List[str]
    notifications: List[str]
