from fastapi import APIRouter, Depends
from typing import List
from app.schemas import User
from app.services.auth_service import require_role
from app.services.admin_service import AdminService

router = APIRouter()

@router.get("/users", response_model=List[User])
async def list_users(user=Depends(require_role(["Administrator"]))):
    service = AdminService(user=user)
    users = await service.list_users()
    return users

@router.post("/programs/permissions")
async def update_permissions(user_id: str, roles: List[str], user=Depends(require_role(["Administrator"]))):
    service = AdminService(user=user)
    success = await service.update_user_roles(user_id, roles)
    return {"updated": success}
