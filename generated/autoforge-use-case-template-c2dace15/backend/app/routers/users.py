from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.user import UserResponse
from ..core.auth import get_current_active_user, require_roles
from ..services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user = Depends(get_current_active_user)):
    return current_user

@router.get("/", response_model=List[UserResponse])
async def list_users(current_user = Depends(require_roles(["admin", "coordinator"]))):
    users = UserService.get_all_users()
    return users
