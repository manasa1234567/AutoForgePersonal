from fastapi import APIRouter, Depends, HTTPException, status
from app.models import FeedbackSubmission
from app.dependencies import get_current_user
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/submit", status_code=201)
async def submit_feedback(
    feedback: FeedbackSubmission,
    user=Depends(get_current_user),
    service: FeedbackService = Depends()
):
    # Validate required fields automatically by Pydantic
    try:
        await service.submit_feedback(user.id, feedback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Feedback submitted successfully"}
