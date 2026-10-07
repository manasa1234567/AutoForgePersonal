from pydantic import BaseModel, Field, constr
from typing import Optional, List
from datetime import date

# User roles
class User(BaseModel):
    username: str
    roles: List[str]

# Training Program Schemas
class TrainingProgramBase(BaseModel):
    title: constr(min_length=1)
    description: Optional[str]

class TrainingProgramCreate(TrainingProgramBase):
    pass

class TrainingProgramRead(TrainingProgramBase):
    id: int
    active: bool

    class Config:
        orm_mode = True

# Feedback Schemas
class FeedbackBase(BaseModel):
    session_id: int
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str]

    def is_complete(self) -> bool:
        return self.rating is not None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    employee_username: str

    class Config:
        orm_mode = True
