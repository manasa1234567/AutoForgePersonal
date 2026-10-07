from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.onboarding import OnboardingTaskRead, OnboardingTaskUpdate
from app.services.onboarding_service import OnboardingService
from app.api.auth_router import get_current_user, User

router = APIRouter()

@router.get("/tasks", response_model=List[OnboardingTaskRead])
async def get_onboarding_tasks(current_user: User = Depends(get_current_user)):
    tasks = await OnboardingService.get_tasks_for_user(current_user)
    return tasks

@router.put("/tasks/{task_id}", response_model=OnboardingTaskRead)
async def update_onboarding_task(task_id: int, task_update: OnboardingTaskUpdate, current_user: User = Depends(get_current_user)):
    updated_task = await OnboardingService.update_task_status(task_id, task_update, current_user)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found or no permission.")
    return updated_task
