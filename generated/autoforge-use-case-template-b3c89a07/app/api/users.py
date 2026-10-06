from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import User, UserUpdate
from app.services.auth import get_current_user, require_role
from app.services.users import get_all_users, update_user

router = APIRouter()

@router.get("/", response_model=List[User])
async def list_users(current_user=Depends(require_role("administrator"))):
    return await get_all_users()

@router.put("/{user_id}", response_model=User)
async def update_user_info(user_id: int, user_update: UserUpdate, current_user=Depends(require_role("administrator"))):
    user = await update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
