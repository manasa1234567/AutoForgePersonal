import asyncio
from typing import Dict, List

class SessionsService:

    def __init__(self):
        # In-memory session registration and attendance storage as placeholder
        self._session_capacity = {1: 20}  # session_id: capacity
        self._registrations: Dict[int, List[int]] = {1: [2]}  # session_id: list of user_ids
        self._attendance: Dict[int, Dict[int, bool]] = {}  # session_id -> user_id -> bool

    async def register_user_to_session(self, user_id: int, session_id: int):
        capacity = self._session_capacity.get(session_id)
        if capacity is None:
            raise ValueError("Session not found")
        registered_users = self._registrations.setdefault(session_id, [])
        if len(registered_users) >= capacity:
            raise ValueError("Session capacity reached")
        if user_id in registered_users:
            raise ValueError("User already registered")
        registered_users.append(user_id)
        await asyncio.sleep(0.05)  # simulate DB write

    async def mark_attendance(self, session_id: int, user_id: int, attended: bool):
        if session_id not in self._registrations or user_id not in self._registrations[session_id]:
            raise ValueError("User not registered for session")
        att_map = self._attendance.setdefault(session_id, {})
        att_map[user_id] = attended
        await asyncio.sleep(0.05)  # simulate DB write
