from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    session_id: int
    employee_id: int
    rating: int
    comments: Optional[str]

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
