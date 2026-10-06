from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.dashboard import DashboardData, ProgramSummary
from app.services.auth import get_current_user
from app.services.dashboard import get_dashboard_data_for_user

router = APIRouter()

@router.get("/", response_model=DashboardData)
async def read_dashboard(current_user=Depends(get_current_user)):
    try:
        data = await get_dashboard_data_for_user(current_user)
        return data
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Dashboard data unavailable: {str(e)}")
