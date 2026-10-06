from pydantic import BaseModel
from typing import List

class ProgramSummary(BaseModel):
    program_id: int
    name: str
    completion_rate: float
    assigned_courses: int
    active: bool

class DashboardData(BaseModel):
    total_learners: int
    active_programs: List[ProgramSummary]
    completion_rate_percent: float
    upcoming_sessions_count: int
    attendance_trend: List[int]  # e.g. recent attendance counts
    feedback_rating_avg: float
    recent_activities: List[str]  # titles or summaries
    top_performing_learners: List[str]  # names
    notifications: List[str]

