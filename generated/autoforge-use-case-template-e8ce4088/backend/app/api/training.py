from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas import TrainingProgramCreate, TrainingProgram, Session, SessionCreate, AttendanceRecord, FeedbackSubmit
from ..api.auth import get_current_user, User

router = APIRouter()

# In-memory placeholder storage
programs = {}
sessions = {}
attendance_records = {}  # session_id -> dict user_id -> bool
feedbacks = {}  # session_id -> list of FeedbackSubmit
registrations = {}  # session_id -> set of user_ids who have registered


def user_has_role(user: User, roles: List[str]) -> bool:
    return any(role in user.roles for role in roles)


@router.post("/programs", response_model=TrainingProgram, status_code=status.HTTP_201_CREATED)
async def create_training_program(program: TrainingProgramCreate, current_user: User = Depends(get_current_user)):
    # Only Learning Program Coordinators or Admins can create new programs
    allowed_roles = ["Administrator", "Manager"]
    if not user_has_role(current_user, allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if program.id in programs:
        raise HTTPException(status_code=400, detail="Program with this ID already exists")
    programs[program.id] = TrainingProgram(**program.dict())
    return programs[program.id]


@router.get("/programs", response_model=List[TrainingProgram])
async def list_training_programs(current_user: User = Depends(get_current_user)):
    # Any authenticated user can list training programs
    return list(programs.values())


@router.post("/sessions", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(session: SessionCreate, current_user: User = Depends(get_current_user)):
    # Only Trainers/Mentors or Admin can create sessions
    allowed_roles = ["Administrator", "Trainer", "Mentor"]
    if not user_has_role(current_user, allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if session.id in sessions:
        raise HTTPException(status_code=400, detail="Session with this ID already exists")
    # Check if program exists
    if session.program_id not in programs:
        raise HTTPException(status_code=404, detail="Associated training program not found")
    new_session = Session(**session.dict())
    sessions[session.id] = new_session
    registrations[session.id] = set()
    return new_session


@router.get("/sessions", response_model=List[Session])
async def list_sessions(current_user: User = Depends(get_current_user)):
    # Any authenticated user can list sessions
    return list(sessions.values())


@router.post("/sessions/{session_id}/attendance", status_code=status.HTTP_204_NO_CONTENT)
async def mark_attendance(session_id: str, attendance: AttendanceRecord, current_user: User = Depends(get_current_user)):
    # Only Trainer/Mentor or Admin can mark attendance
    allowed_roles = ["Administrator", "Trainer", "Mentor"]
    if not user_has_role(current_user, allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Check session
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    # Update attendance
    attendance_records.setdefault(session_id, {})[attendance.user_id] = attendance.present
    return


@router.post("/sessions/{session_id}/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(session_id: str, feedback: FeedbackSubmit, current_user: User = Depends(get_current_user)):
    # Only attendees (Employee) or Admin can submit feedback
    allowed_roles = ["Employee", "Administrator"]
    if not user_has_role(current_user, allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate required fields are enforced by Pydantic
    # Enforce user_id in feedback matches current_user.username
    if feedback.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Cannot submit feedback for another user")

    feedbacks.setdefault(session_id, []).append(feedback)
    return {"message": "Feedback submitted successfully"}


@router.post("/sessions/{session_id}/register", status_code=status.HTTP_201_CREATED)
async def register_for_session(session_id: str, current_user: User = Depends(get_current_user)):
    # Only Employees allowed to register
    allowed_roles = ["Employee"]
    if not user_has_role(current_user, allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    registrants = registrations.setdefault(session_id, set())

    # Check capacity
    if len(registrants) >= session.capacity:
        raise HTTPException(status_code=400, detail="Session capacity reached. Registration blocked.")

    # Register user
    if current_user.username in registrants:
        # Already registered - allow idempotent success
        return {"message": "Already registered"}

    registrants.add(current_user.username)
    return {"message": "Registration successful"}
