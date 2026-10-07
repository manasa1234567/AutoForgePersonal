from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import UserBase, UserCreate
from app.dependencies import get_current_user
from app.services.users_service import UsersService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserBase)
async def get_current_user_profile(user=Depends(get_current_user)):
    return user

@router.get("/", response_model=List[UserBase])
async def list_users(user=Depends(get_current_user), service: UsersService = Depends()):
    # Only admins can list all users
    if user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    users = await service.list_all_users()
    return users

@router.post("/", status_code=201, response_model=UserBase)
async def create_user(user_create: UserCreate, user=Depends(get_current_user), service: UsersService = Depends()):
    if user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    created_user = await service.create_user(user_create)
    return created_user
