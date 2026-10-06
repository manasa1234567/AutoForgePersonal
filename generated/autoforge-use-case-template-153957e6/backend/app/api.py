from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
from typing import List, Optional
from uuid import uuid4
from enum import Enum

# Role strings standardized to match frontend and requirements
class Role(str, Enum):
    Employee = "Employee"
    Trainer = "Trainer"
    Mentor = "Mentor"
    Manager = "Manager"
    Administrator = "Administrator"
    LearningProgramCoordinator = "Learning Program Coordinator"

class User(BaseModel):
    id: str
    name: str
    email: str
    role: Role

class TrainingProgram(BaseModel):
    id: str
    title: constr(min_length=1)
    description: Optional[str] = None
    completion_percentage: float = 0.0

class Session(BaseModel):
    session_id: str
    program_id: str
    title: constr(min_length=1)
    start: str
    capacity: int
    registered_count: int

class AttendanceRecord(BaseModel):
    id: str
    participant_id: str
    participant_name: str
    present: bool

class SessionAttendance(BaseModel):
    session_id: str
    session_title: str
    records: List[AttendanceRecord]

class FeedbackSubmission(BaseModel):
    rating: int
    comments: Optional[str] = None

class LearnerAnalytics(BaseModel):
    id: str
    name: str
    completion_rate: float

class AnalyticsData(BaseModel):
    total_learners: int
    active_programs: int
    completion_rate: float
    upcoming_sessions: List[Session]
    attendance_trend: List[dict]
    feedback_ratings: List[dict]
    recent_activities: List[str]
    top_performers: List[LearnerAnalytics]
    notifications: List[str]

# Mock Data
users = [
    User(id="user_1", name="Alice Employee", email="alice@example.com", role=Role.Employee),
    User(id="user_2", name="Bob Trainer", email="bob@example.com", role=Role.Trainer),
    User(id="user_3", name="Carol Manager", email="carol@example.com", role=Role.Manager),
    User(id="user_4", name="Dave Admin", email="dave@example.com", role=Role.Administrator),
    User(id="user_5", name="Eve Coordinator", email="eve@example.com", role=Role.LearningProgramCoordinator),
]

training_programs = [
    TrainingProgram(id="prog_1", title="Onboarding Basics", description="Employee onboarding program", completion_percentage=45.0),
    TrainingProgram(id="prog_2", title="Advanced Sales", description="Sales techniques and tips", completion_percentage=80.0),
]

sessions = [
    Session(session_id="sess_1", program_id="prog_1", title="Orientation", start="2024-06-15T09:00:00Z", capacity=30, registered_count=28),
    Session(session_id="sess_2", program_id="prog_2", title="Negotiation Skills", start="2024-06-20T13:00:00Z", capacity=20, registered_count=20),
]

attendance_records = {
    "sess_1": [
        AttendanceRecord(id="att1", participant_id="user_1", participant_name="Alice Employee", present=True),
    ],
    "sess_2": [
        AttendanceRecord(id="att2", participant_id="user_1", participant_name="Alice Employee", present=False),
    ],
}

feedback_storage = {}

app = FastAPI()

# Restrict CORS to frontend app origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: simulate get current user
# NOTE: Authentication with Microsoft Entra ID / Azure AD must be added in production
async def get_current_user() -> User:
    # For demo, allow role to be overridden by X-User-Role header for testing
    # Default to Alice Employee
    # Replace with proper OpenID Connect token validation for real SSO integration
    from fastapi import Request
    async def _inner(request: Request):
        header_role = request.headers.get("x-user-role")
        if header_role:
            for u in users:
                if u.role == header_role:
                    return u
        return users[0]
    return await _inner

async def require_role(user: User, allowed_roles: List[Role]):
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

@app.get('/api/dashboard')
async def get_dashboard_data(user: User = Depends(get_current_user())):
    # Return dashboard data filtered by user role
    # For demo: all programs and analytics for every role

    analytics_data = AnalyticsData(
        total_learners=120,
        active_programs=3,
        completion_rate=67.4,
        upcoming_sessions=sessions,
        attendance_trend=[{"label": "Week 22", "value": 80}, {"label": "Week 23", "value": 85}],
        feedback_ratings=[{"label": "Positive", "value": 70}, {"label": "Neutral", "value": 20}, {"label": "Negative", "value": 10}],
        recent_activities=["Alice completed Onboarding Basics", "Bob marked attendance"],
        top_performers=[LearnerAnalytics(id="user_1", name="Alice Employee", completion_rate=95.0)],
        notifications=["New program created: Leadership Training"],
    )

    attendances = []
    if user.role in [Role.Trainer, Role.Mentor]:
        for sess_id in attendance_records.keys():
            attendances.append(
                SessionAttendance(
                    session_id=sess_id,
                    session_title=[s.title for s in sessions if s.session_id == sess_id][0],
                    records=attendance_records[sess_id],
                )
            )

    # Programs filtered: employee sees assigned (all here), others see all
    programs_for_user = training_programs

    return {
        "programs": programs_for_user,
        "analytics": analytics_data.dict(),
        "attendances": [a.dict() for a in attendances],
    }

# Server send events simplified
from fastapi.responses import StreamingResponse
import asyncio

async def event_generator():
    while True:
        await asyncio.sleep(10)  # 10s refresh sim
        yield "data: update\n\n"

@app.get('/api/dashboard/updates')
async def dashboard_updates():
    return StreamingResponse(event_generator(), media_type="text/event-stream")

class CreateProgramRequest(BaseModel):
    title: constr(min_length=1)
    description: Optional[str] = None

@app.post('/api/programs')
async def create_program(request: CreateProgramRequest, user: User = Depends(get_current_user())):
    await require_role(user, [Role.LearningProgramCoordinator, Role.Administrator])
    new_id = f"prog_{uuid4()}"
    new_program = TrainingProgram(id=new_id, title=request.title, description=request.description)
    training_programs.append(new_program)
    return new_program

@app.post('/api/programs/{program_id}/feedback')
async def submit_feedback(program_id: str, feedback: FeedbackSubmission, user: User = Depends(get_current_user())):
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    feedback_storage[(user.id, program_id)] = feedback
    return {"message": "Feedback submitted successfully"}

@app.get('/api/programs/{program_id}/attendance')
async def get_attendance(program_id: str, user: User = Depends(get_current_user())):
    await require_role(user, [Role.Trainer, Role.Mentor, Role.Administrator])
    sess = next((s for s in sessions if s.program_id == program_id), None)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    records = attendance_records.get(sess.session_id, [])
    attendance = SessionAttendance(session_id=sess.session_id, session_title=sess.title, records=records)
    return attendance

class AttendanceUpdateRequest(BaseModel):
    present: bool

@app.post('/api/programs/{program_id}/attendance/{attendance_id}')
async def update_attendance(program_id: str, attendance_id: str, update_req: AttendanceUpdateRequest, user: User = Depends(get_current_user())):
    await require_role(user, [Role.Trainer, Role.Mentor, Role.Administrator])

    for rec_list in attendance_records.values():
        for rec in rec_list:
            if rec.id == attendance_id:
                rec.present = update_req.present
                return {"message": "Attendance updated"}
    raise HTTPException(status_code=404, detail="Attendance record not found")

@app.post('/api/sessions/{session_id}/register')
async def register_session(session_id: str, user: User = Depends(get_current_user())):
    sess = next((s for s in sessions if s.session_id == session_id), None)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.registered_count >= sess.capacity:
        raise HTTPException(status_code=409, detail="Session is full")
    sess.registered_count += 1
    return {"message": "Registered successfully"}

@app.get('/api/admin/users')
async def list_users(user: User = Depends(get_current_user())):
    await require_role(user, [Role.Administrator])
    return users

@app.get('/api/admin/programs')
async def list_programs(user: User = Depends(get_current_user())):
    await require_role(user, [Role.Administrator])
    return training_programs

@app.get('/')
async def root():
    return {"message": "Learning Management System API is running"}
