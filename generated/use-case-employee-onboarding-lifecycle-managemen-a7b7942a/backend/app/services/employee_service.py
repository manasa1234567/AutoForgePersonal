from typing import List, Optional
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from datetime import date

# Dummy in-memory DB substitute
_emp_db = {}
_emp_id_seq = 1

class EmployeeService:

    @staticmethod
    async def get_employees_for_user(user) -> List[EmployeeRead]:
        # For demo return all active employees
        employees = [emp for emp in _emp_db.values() if emp['is_active']]
        return [EmployeeRead(**emp) for emp in employees]

    @staticmethod
    async def create_employee(employee_data: EmployeeCreate) -> EmployeeRead:
        global _emp_id_seq
        emp_id = _emp_id_seq
        _emp_id_seq += 1
        emp_dict = employee_data.dict()
        emp_dict.update({"employee_id": emp_id, "is_active": True})
        _emp_db[emp_id] = emp_dict
        # TODO: trigger onboarding workflow
        return EmployeeRead(**emp_dict)

    @staticmethod
    async def get_employee(employee_id: int) -> Optional[EmployeeRead]:
        emp = _emp_db.get(employee_id)
        if emp and emp['is_active']:
            return EmployeeRead(**emp)
        return None

    @staticmethod
    async def update_employee(employee_id: int, employee_update: EmployeeUpdate) -> Optional[EmployeeRead]:
        emp = _emp_db.get(employee_id)
        if not emp or not emp["is_active"]:
            return None
        update_data = employee_update.dict(exclude_unset=True)
        emp.update(update_data)
        _emp_db[employee_id] = emp
        return EmployeeRead(**emp)

    @staticmethod
    async def soft_delete_employee(employee_id: int) -> bool:
        emp = _emp_db.get(employee_id)
        if not emp or not emp["is_active"]:
            return False
        emp["is_active"] = False
        _emp_db[employee_id] = emp
        return True
