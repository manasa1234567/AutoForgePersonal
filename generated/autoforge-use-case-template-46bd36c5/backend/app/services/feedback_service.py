from app.models import FeedbackSubmission
import asyncio

class FeedbackService:

    def __init__(self):
        # Placeholder for database or external storage
        self._feedback_storage = []

    async def submit_feedback(self, user_id: int, feedback: FeedbackSubmission):
        # Check required rating
        if not (1 <= feedback.rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        # Simulate saving feedback
        record = {
            "user_id": user_id,
            "session_id": feedback.session_id,
            "rating": feedback.rating,
            "comments": feedback.comments
        }
        self._feedback_storage.append(record)
        # Simulate async DB save delay
        await asyncio.sleep(0.05)
        # No error means success
        return
