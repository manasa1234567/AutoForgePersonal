from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    id: str
    name: str
    email: str
    roles: List[str]


class AssignedProgram(BaseModel):
    program_id: str
    program_name: str
    completion_percentage: float = Field(..., ge=0, le=100)
    status: constr(min_length=1)  # e.g., "In Progress", "Completed"


class FeedbackCreate(BaseModel):
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[constr(max_length=1000)] = None


class AttendanceMark(BaseModel):
    session_id: str
    participant_id: str
    present: bool


class DashboardWidgetBase(BaseModel):
    name: str
    value: Optional[str]


class DashboardData(BaseModel):
    total_learners: int
    active_programs: int
    completion_rate_percent: float
    upcoming_sessions: List[str]
    attendance_trend_chart_data: List[float]
    feedback_rating_chart_data: List[float]
    recent_activities: List[str]
    top_performing_learners: List[str]
    notifications: List[str]
    quick_actions: List[str]


class TeamAnalytics(BaseModel):
    attendance_percentage: float
    completion_rate: float
    feedback_trends: List[float]


# Admin models

class UserSummary(BaseModel):
    id: str
    name: str
    email: str
    roles: List[str]


class UserCreate(BaseModel):
    name: str
    email: str
    roles: List[str]


class ProgramSummary(BaseModel):
    id: str
    name: str
    description: Optional[str]

