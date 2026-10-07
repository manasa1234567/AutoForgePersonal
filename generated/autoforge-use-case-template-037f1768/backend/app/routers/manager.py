from fastapi import APIRouter, Depends
from app.services.auth_service import require_role
from app.services.manager_service import ManagerService

router = APIRouter()

@router.get("/team-analytics")
async def get_team_analytics(user=Depends(require_role(["Manager"]))):
    service = ManagerService(user=user)
    analytics = await service.get_team_analytics()
    return analytics
