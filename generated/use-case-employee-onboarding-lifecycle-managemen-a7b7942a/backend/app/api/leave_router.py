from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.leave import LeaveCreate, LeaveRead, LeaveUpdate
from app.services.leave_service import LeaveService
from app.api.auth_router import get_current_user, User

router = APIRouter()

@router.get("/requests", response_model=List[LeaveRead])
async def get_leave_requests(current_user: User = Depends(get_current_user)):
    leaves = await LeaveService.get_leaves_for_user(current_user)
    return leaves

@router.post("/requests", response_model=LeaveRead, status_code=status.HTTP_201_CREATED)
async def create_leave_request(leave: LeaveCreate, current_user: User = Depends(get_current_user)):
    leave_req = await LeaveService.create_leave_request(leave, current_user)
    return leave_req

@router.put("/requests/{leave_id}", response_model=LeaveRead)
async def update_leave_request(leave_id: int, leave_update: LeaveUpdate, current_user: User = Depends(get_current_user)):
    updated = await LeaveService.update_leave_request(leave_id, leave_update, current_user)
    if not updated:
        raise HTTPException(status_code=404, detail="Leave request not found or not authorized.")
    return updated
