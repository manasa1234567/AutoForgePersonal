from pydantic import BaseModel, constr
from typing import Optional
from datetime import date

class EquipmentBase(BaseModel):
    serial_number: constr(min_length=1, max_length=100)
    laptop_model: constr(min_length=1, max_length=100)
    assigned_to: Optional[int] = None  # employee_id
    purchase_date: Optional[date] = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(EquipmentBase):
    assigned_to: Optional[int] = None

class EquipmentRead(EquipmentBase):
    device_id: int

    class Config:
        orm_mode = True
