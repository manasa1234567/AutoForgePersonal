from typing import List
from app.schemas import TrainingProgramRead, FeedbackCreate, Feedback
from app.services.auth_service import User

class EmployeeService:
    def __init__(self, user: User):
        self.user = user

    async def get_assigned_programs(self) -> List[TrainingProgramRead]:
        # TODO: Fetch from DB based on user
        # Simulated response:
        program = TrainingProgramRead(id=1, title="Data Security", description="Security Training", active=True)
        return [program]

    async def submit_feedback(self, feedback_create: FeedbackCreate) -> Feedback:
        # TODO: Save feedback into DB
        feedback = Feedback(id=1, employee_username=self.user.username, **feedback_create.dict())
        return feedback
