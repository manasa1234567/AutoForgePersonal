from fastapi import APIRouter, Depends
from app.services.auth import get_current_user, require_role
from app.services.reports import get_manager_report
from app.models.report import ManagerReport

router = APIRouter()

@router.get("/manager", response_model=ManagerReport)
async def manager_report(current_user=Depends(require_role("manager"))):
    data = await get_manager_report(current_user)
    return data
