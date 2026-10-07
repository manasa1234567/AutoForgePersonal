from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import TrainingProgramRead, FeedbackCreate, Feedback
from app.services.auth_service import get_current_user, User
from app.services.employee_service import EmployeeService

router = APIRouter()

@router.get("/programs", response_model=List[TrainingProgramRead])
async def get_assigned_programs(current_user: User = Depends(get_current_user)):
    """Get logged in employee's assigned training programs and progress"""
    service = EmployeeService(user=current_user)
    programs = await service.get_assigned_programs()
    return programs

@router.post("/feedback", response_model=Feedback)
async def submit_feedback(feedback_create: FeedbackCreate, current_user: User = Depends(get_current_user)):
    """Submit feedback for a completed training session"""
    if not feedback_create.is_complete():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback form is incomplete. Please fill all required fields."
        )
    service = EmployeeService(user=current_user)
    feedback = await service.submit_feedback(feedback_create)
    return feedback
