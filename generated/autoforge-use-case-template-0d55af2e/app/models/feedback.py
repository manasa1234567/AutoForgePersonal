from datetime import datetime
from pydantic import BaseModel, constr
from typing import Optional

class FeedbackBase(BaseModel):
    session_id: int
    user_id: int
    rating: int
    comments: Optional[constr(strip_whitespace=True)] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    submitted_at: datetime

    class Config:
        orm_mode = True
