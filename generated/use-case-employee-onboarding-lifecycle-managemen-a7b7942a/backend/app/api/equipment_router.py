from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate
from app.services.equipment_service import EquipmentService
from app.api.auth_router import get_current_user, User

router = APIRouter()

@router.get("/", response_model=List[EquipmentRead])
async def list_equipment(current_user: User = Depends(get_current_user)):
    # Only IT admins and HR admins can see all
    if not (current_user.is_it_admin or current_user.is_hr_admin):
        raise HTTPException(status_code=403, detail="Not authorized.")
    equipment = await EquipmentService.list_all()
    return equipment

@router.post("/", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)
async def add_equipment(equipment: EquipmentCreate, current_user: User = Depends(get_current_user)):
    if not current_user.is_it_admin:
        raise HTTPException(status_code=403, detail="Not authorized.")
    created = await EquipmentService.add_equipment(equipment)
    return created

@router.put("/{equipment_id}", response_model=EquipmentRead)
async def update_equipment(equipment_id: int, equipment_update: EquipmentUpdate, current_user: User = Depends(get_current_user)):
    if not current_user.is_it_admin:
        raise HTTPException(status_code=403, detail="Not authorized.")
    updated = await EquipmentService.update_equipment(equipment_id, equipment_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Equipment not found.")
    return updated

@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(equipment_id: int, current_user: User = Depends(get_current_user)):
    if not current_user.is_it_admin:
        raise HTTPException(status_code=403, detail="Not authorized.")
    deleted = await EquipmentService.delete_equipment(equipment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Equipment not found.")
    return None
