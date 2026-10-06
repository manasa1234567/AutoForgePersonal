from typing import List, Optional
from app.models.user import User, UserUpdate

# Example in-memory user store
_users = [
    User(id=1, username="jane.employee@company.com", full_name="Jane Employee", email="jane.employee@company.com", roles=["employee"]),
    User(id=2, username="bob.trainer@company.com", full_name="Bob Trainer", email="bob.trainer@company.com", roles=["trainer"]),
    User(id=3, username="alice.manager@company.com", full_name="Alice Manager", email="alice.manager@company.com", roles=["manager"]),
    User(id=4, username="admin@company.com", full_name="Admin User", email="admin@company.com", roles=["administrator"]),
]

async def get_all_users() -> List[User]:
    return _users

async def update_user(user_id: int, user_update: UserUpdate) -> Optional[User]:
    for u in _users:
        if u.id == user_id:
            if user_update.full_name is not None:
                u.full_name = user_update.full_name
            if user_update.email is not None:
                u.email = user_update.email
            if user_update.roles is not None:
                u.roles = user_update.roles
            return u
    return None
