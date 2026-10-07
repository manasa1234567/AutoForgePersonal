from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum
from datetime import datetime

class Role(str, Enum):
    employee = "Employee"
    coordinator = "Learning Program Coordinator"
    trainer = "Trainer/Mentor"
    manager = "Manager"
    administrator = "Administrator"

class UserBase(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: Role

class CourseBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

class ProgramBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class SessionBase(BaseModel):
    id: int
    program_id: int
    title: str
    scheduled_start: datetime
    scheduled_end: datetime
    capacity: int
    attendees_ids: Optional[List[int]] = []

class FeedbackBase(BaseModel):
    id: int
    session_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

class AttendanceBase(BaseModel):
    session_id: int
    user_id: int
    attended: bool

class DashboardWidgets(BaseModel):
    total_learners: int
    active_programs: int
    completion_rate_percent: float
    upcoming_sessions: List[SessionBase]
    attendance_trend: List[int]
    feedback_rating_trend: List[float]
    recent_activities: List[str]
    top_performing_learners: List[UserBase]
    notifications: List[str]

class FeedbackSubmission(BaseModel):
    session_id: int
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

class RegisterSessionRequest(BaseModel):
    session_id: int

class AttendanceMarkRequest(BaseModel):
    session_id: int
    user_id: int
    attended: bool

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: Role

class ProgramCreate(BaseModel):
    name: str
    description: Optional[str] = None
