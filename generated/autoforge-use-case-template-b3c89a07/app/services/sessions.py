from typing import List, Tuple
from app.models.session import SessionInfo

# Example in-memory session data to simulate DB
_sessions = [
    SessionInfo(session_id=1, program_name="Safety Training", course_name="Fire Safety", date="2024-07-01T10:00:00Z", capacity=30, registered_count=29, status="Scheduled"),
    SessionInfo(session_id=2, program_name="Compliance", course_name="HIPAA Basics", date="2024-07-05T15:00:00Z", capacity=20, registered_count=20, status="Scheduled"),
    SessionInfo(session_id=3, program_name="Safety Training", course_name="First Aid", date="2024-07-10T09:00:00Z", capacity=25, registered_count=10, status="Scheduled"),
]

# Per-user registrations, user_id -> set of session_ids
_user_registrations = {}

async def list_sessions(user) -> List[SessionInfo]:
    # Return all sessions for simplicity, real app may filter by user assignments
    return _sessions

async def register_for_session(user_id: str, session_id: int) -> Tuple[bool, str]:
    # Find session
    session = next((s for s in _sessions if s.session_id == session_id), None)
    if not session:
        return False, "Session not found"
    # Check capacity
    if session.registered_count >= session.capacity:
        return False, "Session capacity reached"
    # Check if user already registered
    registered = _user_registrations.get(user_id, set())
    if session_id in registered:
        return False, "Already registered for this session"
    # Register user
    registered.add(session_id)
    _user_registrations[user_id] = registered
    session.registered_count += 1
    return True, "Registered"