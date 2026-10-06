from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.session import TrainingSession, TrainingSessionCreate, TrainingSessionWithAttendance
from app.models.user import UserBase
from app.api.deps import verify_token
from app.services.session_service import (
    get_sessions_for_user,
    create_session,
    register_user_to_session,
    mark_attendance
)

router = APIRouter()

@router.get("/", response_model=List[TrainingSessionWithAttendance])
async def list_sessions(user: UserBase = Depends(verify_token)):
    return await get_sessions_for_user(user)

@router.post("/register/{session_id}", response_model=dict)
async def register_session(session_id: int, user: UserBase = Depends(verify_token)):
    success, msg = await register_user_to_session(user.id, session_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@router.post("/attendance/{session_id}", response_model=dict)
async def attendance(session_id: int, user: UserBase = Depends(verify_token)):
    success, msg = await mark_attendance(user, session_id)
    if not success:
        raise HTTPException(status_code=403, detail=msg)
    return {"message": msg}
