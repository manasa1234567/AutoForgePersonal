from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.session import SessionRegistrationRequest, SessionInfo
from app.services.auth import get_current_user
from app.services.sessions import list_sessions, register_for_session

router = APIRouter()

@router.get("/", response_model=List[SessionInfo])
async def get_sessions(current_user=Depends(get_current_user)):
    return await list_sessions(current_user)

@router.post("/register", status_code=201)
async def register_session(request: SessionRegistrationRequest, current_user=Depends(get_current_user)):
    can_register, message = await register_for_session(current_user.id, request.session_id)
    if not can_register:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "Successfully registered for the session."}
