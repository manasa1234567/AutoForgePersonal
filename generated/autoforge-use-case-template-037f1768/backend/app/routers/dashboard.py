from fastapi import APIRouter, Depends
from app.services.auth_service import get_current_user
from app.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics(user=Depends(get_current_user)):
    service = DashboardService(user=user)
    return await service.get_metrics()
