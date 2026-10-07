from typing import List
from app.schemas import User
from app.services.auth_service import User as AuthUser

class AdminService:
    def __init__(self, user: AuthUser):
        self.user = user

    async def list_users(self) -> List[User]:
        # TODO: Load user list from DB
        return []

    async def update_user_roles(self, user_id: str, roles: List[str]) -> bool:
        # TODO: Update roles in DB
        return True
