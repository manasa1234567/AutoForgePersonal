from typing import List, Optional
from app.schemas.leave import LeaveCreate, LeaveRead, LeaveUpdate, LeaveStatus
from app.api.auth_router import User

_leave_db = {}
_leave_id_seq = 1

class LeaveService:

    @staticmethod
    async def get_leaves_for_user(user: User) -> List[LeaveRead]:
        # HR Admin sees all, manager sees assigned, employee sees own
        if user.is_hr_admin:
            leaves = _leave_db.values()
        else:
            # Simplify: own leaves
            leaves = [lv for lv in _leave_db.values() if lv["employee_id"] == user.username]
        return [LeaveRead(**lv) for lv in leaves]

    @staticmethod
    async def create_leave_request(leave: LeaveCreate, user: User) -> LeaveRead:
        global _leave_id_seq
        leave_id = _leave_id_seq
        _leave_id_seq += 1
        leave_data = leave.dict()
        leave_data["leave_id"] = leave_id
        leave_data["status"] = LeaveStatus.pending
        leave_data["manager_remarks"] = None
        _leave_db[leave_id] = leave_data
        return LeaveRead(**leave_data)

    @staticmethod
    async def update_leave_request(leave_id: int, leave_update: LeaveUpdate, user: User) -> Optional[LeaveRead]:
        lv = _leave_db.get(leave_id)
        if not lv:
            return None
        # Only manager or HR Admin can approve
        if not (user.is_hr_admin or user.is_hiring_manager):
            return None
        update_data = leave_update.dict(exclude_unset=True)
        lv.update(update_data)
        _leave_db[leave_id] = lv
        return LeaveRead(**lv)
