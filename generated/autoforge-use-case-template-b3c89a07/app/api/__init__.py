from fastapi import APIRouter

from app.api import auth, dashboard, feedback, sessions, users, reports

api_router = APIRouter()

# Public auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# User functionality routes
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# Admin and manager user and reporting
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
