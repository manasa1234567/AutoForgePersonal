from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import RegisterSessionRequest, AttendanceMarkRequest, SessionBase
from app.dependencies import get_current_user
from app.services.sessions_service import SessionsService

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/register", status_code=201)
async def register_session(
    request: RegisterSessionRequest,
    user=Depends(get_current_user),
    service: SessionsService = Depends()
):
    try:
        await service.register_user_to_session(user.id, request.session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Registered to session successfully"}

@router.post("/attendance", status_code=200)
async def mark_attendance(
    request: AttendanceMarkRequest,
    user=Depends(get_current_user),
    service: SessionsService = Depends()
):
    # Only trainers or admins allowed
    if user.role not in ["trainer", "administrator"]:
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        await service.mark_attendance(request.session_id, request.user_id, request.attended)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Attendance updated"}
