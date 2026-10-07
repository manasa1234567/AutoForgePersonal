from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import User, UserCreate
from typing import List

router = APIRouter()

fake_users_db = {}

@router.get("/", response_model=List[User])
async def list_users():
    # Placeholder
    return list(fake_users_db.values())

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate):
    if user_create.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(**user_create.dict())
    fake_users_db[user.username] = user
    return user
