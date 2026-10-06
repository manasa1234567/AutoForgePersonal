from typing import List
from app.models.user import UserBase, UserRole
from datetime import datetime

# Static data stub for users
_users = [
    UserBase(id=1, username="johndoe", email="john.doe@example.com", full_name="John Doe",
            role=UserRole.employee, is_active=True, date_joined=datetime.now()),
    UserBase(id=2, username="janemanager", email="jane.manager@example.com", full_name="Jane Manager",
            role=UserRole.manager, is_active=True, date_joined=datetime.now()),
]

async def get_user_by_id(user_id: int) -> UserBase | None:
    for u in _users:
        if u.id == user_id:
            return u
    return None

async def get_all_users() -> List[UserBase]:
    return _users

async def create_user(user_data: dict) -> UserBase:
    # Stub: return a new user object
    new_user = UserBase(**user_data)
    _users.append(new_user)
    return new_user
