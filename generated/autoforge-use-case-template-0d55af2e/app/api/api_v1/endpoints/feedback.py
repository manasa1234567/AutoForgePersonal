from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, constr
from typing import Optional
from app.models.user import UserBase
from app.api.deps import verify_token
from app.services.feedback_service import submit_feedback

router = APIRouter()

class FeedbackForm(BaseModel):
    session_id: int
    rating: int
    comments: Optional[constr(strip_whitespace=True)] = None

@router.post("/", response_model=dict)
async def submit_feedback_endpoint(data: FeedbackForm, user: UserBase = Depends(verify_token)):
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    # Basic completeness validation
    if data.session_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    try:
        await submit_feedback(user.id, data.session_id, data.rating, data.comments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")
    return {"message": "Feedback saved successfully."}
