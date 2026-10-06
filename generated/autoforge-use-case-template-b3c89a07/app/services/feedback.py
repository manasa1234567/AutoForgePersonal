import asyncio

# In-memory feedback storage for demo
_feedback_storage = []

async def save_feedback(user_id: str, session_id: int, rating: int, comments: str = None):
    # Simulate DB write or external service call
    _feedback_storage.append({
        "user_id": user_id,
        "session_id": session_id,
        "rating": rating,
        "comments": comments
    })
    # Simulate async delay
    await asyncio.sleep(0.05)
