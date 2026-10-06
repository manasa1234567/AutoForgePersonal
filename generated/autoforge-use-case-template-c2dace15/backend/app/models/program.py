from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class LearningProgramBase(BaseModel):
    title: str
    description: Optional[str]
    coordinator_id: int

class LearningProgramCreate(LearningProgramBase):
    pass

class LearningProgram(LearningProgramBase):
    id: int
    start_date: Optional[date]
    end_date: Optional[date]
    active: bool

    class Config:
        orm_mode = True

class ProgramSessionBase(BaseModel):
    program_id: int
    name: str
    location: Optional[str]
    scheduled_start: Optional[str]
    scheduled_end: Optional[str]
    capacity: int

class ProgramSessionCreate(ProgramSessionBase):
    pass

class ProgramSession(ProgramSessionBase):
    id: int
    attendance_count: int

    class Config:
        orm_mode = True
