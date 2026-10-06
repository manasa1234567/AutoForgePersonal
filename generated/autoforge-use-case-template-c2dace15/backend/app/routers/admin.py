from fastapi import APIRouter, Depends, HTTPException
from ..core.auth import require_roles
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/", dependencies=[Depends(require_roles(["admin"]))])
async def admin_dashboard():
    # For demonstration return dummy data
    return JSONResponse(content={"message": "Admin dashboard: manage users, programs, permissions, reports."})

@router.get("/users")
async def manage_users():
    # To be implemented: list/manage users
    return JSONResponse(content={"message": "User management interface (placeholder)."})
