from typing import List
from app.models import UserBase, UserCreate
import asyncio

class UsersService:

    def __init__(self):
        self._users = [
            UserBase(id=1, name="Admin User", email="admin@example.com", role="administrator"),
            UserBase(id=2, name="Manager User", email="manager@example.com", role="manager"),
            UserBase(id=3, name="Employee User", email="employee@example.com", role="employee"),
            UserBase(id=4, name="Trainer User", email="trainer@example.com", role="trainer"),
        ]

    async def list_all_users(self) -> List[UserBase]:
        await asyncio.sleep(0.01)  # simulate DB
        return self._users

    async def create_user(self, user_create: UserCreate) -> UserBase:
        new_id = max(u.id for u in self._users) + 1
        new_user = UserBase(
            id=new_id,
            name=user_create.name,
            email=user_create.email,
            role=user_create.role
        )
        self._users.append(new_user)
        await asyncio.sleep(0.05)  # simulate DB
        return new_user
