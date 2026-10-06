from typing import List, Tuple
from datetime import datetime, timedelta
from app.models.session import TrainingSession, TrainingSessionCreate, TrainingSessionWithAttendance
from app.models.user import UserBase, UserRole

# Dummy in-memory sessions data
_sessions = [
    TrainingSessionWithAttendance(
        id=101,
        program_id=10,
        title="Intro to Compliance",
        description="Compliance basics",
        start_datetime=datetime.utcnow() + timedelta(days=5),
        end_datetime=datetime.utcnow() + timedelta(days=5, hours=2),
        capacity=20,
        attendees_count=5
    ),
    TrainingSessionWithAttendance(
        id=102,
        program_id=11,
        title="Leadership 101",
        description="Core leadership training",
        start_datetime=datetime.utcnow() + timedelta(days=10),
        end_datetime=datetime.utcnow() + timedelta(days=10, hours=3),
        capacity=15,
        attendees_count=15
    )
]

# Dummy user registrations
_user_sessions = {
    1: [101],  # user_id 1 registered in session 101
}

async def get_sessions_for_user(user: UserBase) -> List[TrainingSessionWithAttendance]:
    # Employees get their sessions
    if user.role == UserRole.employee:
        registered_ids = _user_sessions.get(user.id, [])
        return [s for s in _sessions if s.id in registered_ids]
    # Trainers, managers, admins get all sessions (simplified)
    else:
        return _sessions

async def register_user_to_session(user_id: int, session_id: int) -> Tuple[bool, str]:
    session = next((s for s in _sessions if s.id == session_id), None)
    if not session:
        return False, "Session not found"
    if session.attendees_count >= session.capacity:
        return False, "Session capacity reached"
    user_registered_sessions = _user_sessions.setdefault(user_id, [])
    if session_id in user_registered_sessions:
        return False, "Already registered"
    user_registered_sessions.append(session_id)
    session.attendees_count += 1
    return True, "Registered successfully"

async def mark_attendance(user: UserBase, session_id: int) -> Tuple[bool, str]:
    # Only trainer/manager/admin can mark attendance
    if user.role not in [UserRole.trainer, UserRole.manager, UserRole.administrator]:
        return False, "Insufficient permissions"
    session = next((s for s in _sessions if s.id == session_id), None)
    if not session:
        return False, "Session not found"

    # Dummy: mark attendance in data store
    # Here just allow
    return True, "Attendance marked"
