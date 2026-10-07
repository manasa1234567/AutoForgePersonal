from typing import List, Optional
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate

_equipment_db = {}
_equipment_id_seq = 1

class EquipmentService:

    @staticmethod
    async def list_all() -> List[EquipmentRead]:
        return [EquipmentRead(**eq) for eq in _equipment_db.values()]

    @staticmethod
    async def add_equipment(equipment: EquipmentCreate) -> EquipmentRead:
        global _equipment_id_seq
        eq_id = _equipment_id_seq
        _equipment_id_seq += 1
        eq_dict = equipment.dict()
        eq_dict["device_id"] = eq_id
        _equipment_db[eq_id] = eq_dict
        return EquipmentRead(**eq_dict)

    @staticmethod
    async def update_equipment(equipment_id: int, equipment_update: EquipmentUpdate) -> Optional[EquipmentRead]:
        eq = _equipment_db.get(equipment_id)
        if not eq:
            return None
        update_data = equipment_update.dict(exclude_unset=True)
        eq.update(update_data)
        _equipment_db[equipment_id] = eq
        return EquipmentRead(**eq)

    @staticmethod
    async def delete_equipment(equipment_id: int) -> bool:
        if equipment_id in _equipment_db:
            del _equipment_db[equipment_id]
            return True
        return False
