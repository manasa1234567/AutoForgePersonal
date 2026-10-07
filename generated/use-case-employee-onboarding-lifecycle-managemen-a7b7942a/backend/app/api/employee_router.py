from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.employee_service import EmployeeService
from app.api.auth_router import get_current_user, User

router = APIRouter()

@router.get("/", response_model=List[EmployeeRead])
async def get_all_employees(current_user: User = Depends(get_current_user)):
    # Only HR Admin and Hiring Manager see different lists
    # For simplicity, HR Admin sees all, Hiring Manager sees assigned only
    employees = await EmployeeService.get_employees_for_user(current_user)
    return employees

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate, current_user: User = Depends(get_current_user)):
    # Only HR Admin can create
    if not current_user.is_hr_admin:
        raise HTTPException(status_code=403, detail="Not authorized.")
    created = await EmployeeService.create_employee(employee)
    return created

@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: int, current_user: User = Depends(get_current_user)):
    emp = await EmployeeService.get_employee(employee_id)
    if emp is None or (not current_user.can_access_employee(employee_id)):
        raise HTTPException(status_code=404, detail="Employee not found or access denied.")
    return emp

@router.put("/{employee_id}", response_model=EmployeeRead)
async def update_employee(employee_id: int, employee_update: EmployeeUpdate, current_user: User = Depends(get_current_user)):
    if not current_user.is_hr_admin:
        raise HTTPException(status_code=403, detail="Not authorized.")
    updated = await EmployeeService.update_employee(employee_id, employee_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return updated

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_employee(employee_id: int, current_user: User = Depends(get_current_user)):
    if not current_user.is_hr_admin:
        raise HTTPException(status_code=403, detail="Not authorized.")
    success = await EmployeeService.soft_delete_employee(employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return None
