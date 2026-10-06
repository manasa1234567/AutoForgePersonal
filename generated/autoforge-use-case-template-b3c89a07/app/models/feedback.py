from pydantic import BaseModel, constr
from typing import Optional

class FeedbackForm(BaseModel):
    session_id: int
    rating: int
    comments: Optional[constr(max_length=500)] = None
