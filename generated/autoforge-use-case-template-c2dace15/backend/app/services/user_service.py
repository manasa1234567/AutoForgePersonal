from typing import Optional
from ..models.user import User
from ..core.auth import fake_users_db

# Fake user service

class UserService:

    @staticmethod
    def get_user(username: str) -> Optional[User]:
        user_dict = fake_users_db.get(username)
        if user_dict:
            return User(**user_dict)
        return None

    @staticmethod
    def get_all_users() -> list[User]:
        return [User(**u) for u in fake_users_db.values()]

    # Additional methods like create, update, delete users to be added later
