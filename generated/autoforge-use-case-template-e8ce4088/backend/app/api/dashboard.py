from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List, Dict
from ..api.auth import get_current_user, User
from ..schemas import DashboardMetrics
from ..api.training import programs, sessions, attendance_records, feedbacks, registrations, user_has_role

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: User = Depends(get_current_user)):
    # Gather data relevant to the user role

    # For simplicity, this example uses in-memory data from training module
    role = None
    if current_user.roles:
        role = current_user.roles[0]
    
    # Calculate total learners (employees) registered
    learners_set = set()
    for reglist in registrations.values():
        learners_set.update(reglist)
    total_learners = len(learners_set)

    active_programs = len(programs)

    # Compute overall completion rate as attendance / capacity for sessions for user's programs
    # Aggregate attendance counts
    total_capacity = 0
    total_attended = 0
    for session in sessions.values():
        total_capacity += session.capacity
        session_attendance = attendance_records.get(session.id, {})
        total_attended += sum(1 for attended in session_attendance.values() if attended)
    completion_rate = (total_attended / total_capacity) if total_capacity > 0 else 0.0

    # Upcoming sessions count (future dates)
    from datetime import date
    today = date.today()
    upcoming_sessions = sum(1 for s in sessions.values() if s.scheduled_date >= today)

    # Attendance trend - dummy last 5 periods
    attendance_trend = [100, 95, 90, 85, 80]

    # Feedback rating - dummy average ratings
    feedback_rating = [4, 3, 5, 4, 4]

    # Recent activities - dummy
    recent_activities: List[str] = []

    # Top performing learners - dummy
    top_performing_learners: List[str] = []

    # Notifications - dummy
    notifications: List[str] = []

    # Customize data for roles could be added here

    return DashboardMetrics(
        total_learners=total_learners,
        active_programs=active_programs,
        completion_rate=completion_rate,
        upcoming_sessions=upcoming_sessions,
        attendance_trend=attendance_trend,
        feedback_rating=feedback_rating,
        recent_activities=recent_activities,
        top_performing_learners=top_performing_learners,
        notifications=notifications,
    )
