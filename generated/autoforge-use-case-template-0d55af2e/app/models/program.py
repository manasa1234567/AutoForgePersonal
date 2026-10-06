from datetime import date
from typing import List, Optional
from pydantic import BaseModel

class LearningProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date

class LearningProgramCreate(LearningProgramBase):
    pass

class LearningProgram(LearningProgramBase):
    id: int
    class Config:
        orm_mode = True
