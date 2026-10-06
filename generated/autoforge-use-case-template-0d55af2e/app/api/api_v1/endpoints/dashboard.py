from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from app.models.user import UserBase, UserRole
from app.api.deps import verify_token
from datetime import datetime

router = APIRouter()

# Dummy data for dashboard widgets
from app.services.dashboard_service import get_dashboard_for_user

@router.get("/", response_model=Any, tags=["dashboard"])
async def get_dashboard(user: UserBase = Depends(verify_token)):
    """Return dashboard data based on user role and permissions."""
    try:
        data = await get_dashboard_for_user(user)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    return data
