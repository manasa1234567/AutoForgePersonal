from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import UserBase, UserRole
from app.api.deps import verify_token, verify_admin
from app.services.user_service import get_user_by_id, get_all_users, create_user

router = APIRouter()

@router.get("/me", response_model=UserBase)
async def read_current_user(user: UserBase = Depends(verify_token)):
    return user

@router.get("/", response_model=List[UserBase])
async def read_users(admin: UserBase = Depends(verify_admin)):
    return await get_all_users()

# Other user management endpoints would go here (create, update, delete users with admin only access)
