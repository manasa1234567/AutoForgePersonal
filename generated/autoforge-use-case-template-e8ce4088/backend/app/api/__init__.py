from fastapi import APIRouter

from .training import router as training_router
from .users import router as users_router
from .dashboard import router as dashboard_router
from .auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(training_router, prefix="/training", tags=["training"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
