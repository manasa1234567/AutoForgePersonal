from pydantic import BaseModel
from typing import List

class ManagerReport(BaseModel):
    attendance_rate: float
    completion_rate: float
    feedback_trends: List[float]
    team_members: List[str]

