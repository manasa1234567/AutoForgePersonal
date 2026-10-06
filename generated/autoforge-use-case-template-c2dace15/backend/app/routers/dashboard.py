from fastapi import APIRouter, Depends, HTTPException
from ..core.auth import get_current_active_user
from fastapi import status

router = APIRouter()

@router.get("/", summary="Get dashboard data")
async def get_dashboard(current_user = Depends(get_current_active_user)):
    user = current_user
    # Simplified static response due to no DB integration
    if "employee" in user.roles:
        data = {
            "total_learners": 1,
            "active_programs": 2,
            "completion_rate": 75.0,
            "upcoming_sessions": [],
            "attendance_trend": [],
            "feedback_rating": [],
            "recent_activities": [],
            "top_performing_learners": [],
            "notifications": [],
            "quick_actions": [],
        }
    elif "manager" in user.roles:
        data = {
            "team_analytics": {
                "attendance": 92.5,
                "completion_rates": 85.3,
                "feedback_trends": [],
            }
        }
    else:
        data = {"message": "Dashboard data for role not implemented in sample."}
    return data
