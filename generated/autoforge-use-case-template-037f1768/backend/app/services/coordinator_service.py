from typing import List
from app.schemas import TrainingProgramCreate, TrainingProgramRead
from app.services.auth_service import User

class CoordinatorService:
    def __init__(self, user: User):
        self.user = user

    async def create_program(self, program_create: TrainingProgramCreate) -> TrainingProgramRead:
        # TODO: Persist to DB
        program = TrainingProgramRead(
            id=123,
            title=program_create.title,
            description=program_create.description,
            active=True
        )
        return program

    async def list_programs(self) -> List[TrainingProgramRead]:
        # TODO: Load from DB
        return []
