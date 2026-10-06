from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.attendance import AttendanceResponse, AttendanceCreate
from ..core.auth import get_current_active_user, require_roles
from datetime import datetime

router = APIRouter()

# In-memory attendance storage
fake_attendance = []

@router.post("/", response_model=AttendanceResponse)
async def mark_attendance(attendance: AttendanceCreate, current_user = Depends(require_roles(["trainer", "mentor", "coordinator", "admin"]))):
    # Check capacity (simplified, no real capacity management here)
    new_id = len(fake_attendance) + 1
    new_attendance = attendance.dict()
    new_attendance["id"] = new_id
    new_attendance["marked_at"] = datetime.utcnow()
    fake_attendance.append(new_attendance)
    # Would update dashboard
    return new_attendance

@router.get("/", response_model=List[AttendanceResponse])
async def list_attendance(current_user = Depends(require_roles(["trainer", "manager", "coordinator", "admin"]))):
    return fake_attendance
