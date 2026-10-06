from fastapi import APIRouter
from app.api.api_v1.endpoints import dashboard, users, sessions, feedback, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
