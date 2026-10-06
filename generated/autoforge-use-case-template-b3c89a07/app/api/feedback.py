from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, constr
from typing import Optional
from app.services.auth import get_current_user
from app.services.feedback import save_feedback

router = APIRouter()

class FeedbackForm(BaseModel):
    session_id: int
    rating: int  # 1 to 5
    comments: Optional[constr(max_length=500)] = None

@router.post("/submit", status_code=201)
async def submit_feedback(form: FeedbackForm, current_user=Depends(get_current_user)):
    # Validate rating range
    if not (1 <= form.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    try:
        await save_feedback(current_user.id, form.session_id, form.rating, form.comments)
        return {"message": "Feedback submitted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")
