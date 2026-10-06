from typing import Optional

# Simulate feedback storage
_feedback_storage = []

async def submit_feedback(user_id: int, session_id: int, rating: int, comments: Optional[str]) -> None:
    # Validate completeness
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5")
    _feedback_storage.append({
        "user_id": user_id,
        "session_id": session_id,
        "rating": rating,
        "comments": comments
    })
    # Simulate report update asynchronously
    return
