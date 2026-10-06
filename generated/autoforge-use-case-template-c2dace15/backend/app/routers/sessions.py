from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.program import ProgramSessionResponse, ProgramSessionCreate
from ..core.auth import get_current_active_user, require_roles

router = APIRouter()

# Fake storage for demo
fake_sessions = [
    {"id": 1, "program_id": 1, "name": "Session 1", "location": "Room A", "scheduled_start": "2024-05-01T09:00:00", "scheduled_end": "2024-05-01T12:00:00", "capacity": 20, "attendance_count": 15},
]

@router.get("/", response_model=List[ProgramSessionResponse])
async def list_sessions(current_user = Depends(get_current_active_user)):
    return fake_sessions

@router.post("/", response_model=ProgramSessionResponse)
async def create_session(session: ProgramSessionCreate, current_user = Depends(require_roles(["coordinator", "admin"]))):
    new_id = len(fake_sessions) + 1
    new_session = session.dict()
    new_session["id"] = new_id
    new_session["attendance_count"] = 0
    fake_sessions.append(new_session)
    return new_session
