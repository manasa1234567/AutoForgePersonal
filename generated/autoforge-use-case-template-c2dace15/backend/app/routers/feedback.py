from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.feedback import FeedbackResponse, FeedbackCreate
from ..core.auth import get_current_active_user, require_roles
from datetime import datetime

router = APIRouter()

# In-memory feedback storage
fake_feedback = []

@router.get("/", response_model=List[FeedbackResponse])
async def list_feedback(current_user = Depends(require_roles(["trainer", "manager", "coordinator", "admin"]))):
    return fake_feedback

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackCreate, current_user = Depends(require_roles(["employee"]))):
    new_id = len(fake_feedback) + 1
    new_feedback = feedback.dict()
    new_feedback.update({"id": new_id, "created_at": datetime.utcnow()})
    fake_feedback.append(new_feedback)
    # In real app, trigger dashboard refresh/event
    return new_feedback
