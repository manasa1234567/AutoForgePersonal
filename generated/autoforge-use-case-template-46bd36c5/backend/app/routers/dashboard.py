from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import (
    DashboardWidgets, UserBase, SessionBase
)
from app.dependencies import get_current_user, get_user_role

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Sample in-memory sample data for demonstration

fake_users = [
    UserBase(id=1, name="Alice Manager", email="alice.manager@example.com", role="manager"),
    UserBase(id=2, name="Bob Employee", email="bob.employee@example.com", role="employee")
]

fake_sessions = [
    SessionBase(
        id=1,
        program_id=1,
        title="Introduction to Python",
        scheduled_start="2024-07-01T09:00:00Z",
        scheduled_end="2024-07-01T12:00:00Z",
        capacity=20,
        attendees_ids=[2]
    )
]

@router.get("/widgets", response_model=DashboardWidgets)
async def get_dashboard_widgets(user: UserBase = Depends(get_current_user)):
    # Dummy implementation with static data to meet requirements
    return DashboardWidgets(
        total_learners=150,
        active_programs=5,
        completion_rate_percent=76.4,
        upcoming_sessions=fake_sessions,
        attendance_trend=[20, 23, 18, 22, 19, 25, 30],
        feedback_rating_trend=[4.1, 4.3, 3.9, 4.5, 4.6, 4.2, 4.7],
        recent_activities=["Bob completed Module 1", "Alice created a new program"],
        top_performing_learners=[fake_users[1]],
        notifications=["New training session available", "System maintenance scheduled"],
    )

@router.get("/sessions/assigned", response_model=List[SessionBase])
async def get_assigned_sessions(user: UserBase = Depends(get_current_user)):
    # Return sessions assigned to the current employee
    if user.role != "employee":
        raise HTTPException(status_code=403, detail="Access denied")
    # Dummy filter
    sessions = [session for session in fake_sessions if user.id in session.attendees_ids]
    return sessions
