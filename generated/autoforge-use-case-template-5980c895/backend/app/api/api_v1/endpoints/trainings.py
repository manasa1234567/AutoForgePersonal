from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, func
from datetime import datetime
from app.core.db import get_db
from app.models.training import TrainingProgram, TrainingSession, Attendance, Feedback
from app.schemas.training import (TrainingProgramRead, TrainingSessionRead, AttendanceRead, FeedbackCreate, FeedbackRead)
from app.api.deps import get_current_active_user, get_current_active_trainer, get_current_active_manager

router = APIRouter()

# Helper functions
async def get_user_programs(db: AsyncSession, user_id: int) -> List[TrainingProgram]:
    # For demo, assume all programs are assigned to all employees
    result = await db.execute(select(TrainingProgram))
    return result.scalars().all()

async def get_completion_percentage(db: AsyncSession, program_id: int, user_id: int) -> float:
    # For demo, calculate a dummy completion %
    # Count sessions in program
    total_sessions = await db.execute(select(func.count(TrainingSession.id)).filter(TrainingSession.program_id == program_id))
    total = total_sessions.scalar() or 0
    if total == 0:
        return 0.0
    # Count attended sessions by user
    attended_sessions = await db.execute(
        select(func.count(Attendance.id))
        .join(TrainingSession)
        .filter(TrainingSession.program_id == program_id)
        .filter(Attendance.user_id == user_id)
        .filter(Attendance.attended == True)
    )
    attended = attended_sessions.scalar() or 0
    return (attended / total) * 100.0

@router.get("/programs", response_model=List[TrainingProgramRead])
async def get_assigned_programs(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    programs = await get_user_programs(db, current_user.id)
    # Build output list including completion percentage
    output = []
    for p in programs:
        completion = await get_completion_percentage(db, p.id, current_user.id)
        program_dict = {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "completion_percentage": completion,
        }
        output.append(program_dict)
    return output

@router.post("/sessions/{session_id}/feedback", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    session_id: int,
    feedback_in: FeedbackCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Validate required fields
    if not (1 <= feedback_in.rating <= 5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5.")
    # Validate session existence
    session = await db.get(TrainingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Check if feedback already submitted by user for the session (optional enhancement)
    existing_feedback = await db.execute(
        select(Feedback).filter(Feedback.session_id == session_id, Feedback.user_id == current_user.id)
    )
    if existing_feedback.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback already submitted for this session.")

    # Save feedback
    fb = Feedback(session_id=session_id, user_id=current_user.id, rating=feedback_in.rating, comments=feedback_in.comments)
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    return fb

@router.post("/sessions/{session_id}/attendance", response_model=AttendanceRead)
async def mark_attendance(
    session_id: int,
    user_id: int = Query(..., description="User ID to mark attendance for."),
    current_user = Depends(get_current_active_trainer),
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(TrainingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Check if attendance record exists for user and session
    attendance_result = await db.execute(
        select(Attendance).filter(Attendance.session_id == session_id, Attendance.user_id == user_id)
    )
    attendance = attendance_result.scalars().first()
    if attendance:
        attendance.attended = True
    else:
        attendance = Attendance(session_id=session_id, user_id=user_id, attended=True)
        db.add(attendance)
    await db.commit()
    await db.refresh(attendance)
    return attendance

@router.get("/team-analytics")
async def get_team_analytics(
    current_user = Depends(get_current_active_manager),
    db: AsyncSession = Depends(get_db)
):
    # Dummy data for demo
    # In real app, implement aggregation over user's team
    data = {
        "attendance_rate": 90.5,
        "completion_rate": 75.0,
        "feedback_average": 4.3,
    }
    return data
