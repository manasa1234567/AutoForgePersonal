from typing import List
from app.services.auth_service import User

class TrainerService:
    def __init__(self, user: User):
        self.user = user

    async def get_participants(self) -> List:
        # TODO: Return participants for trainer's sessions
        return []

    async def record_attendance(self, session_id: int, participant_ids: List[int]) -> bool:
        # TODO: Record attendance in DB
        return True
