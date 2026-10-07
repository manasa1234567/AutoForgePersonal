from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr
import enum

app = FastAPI(
    title="Autoforge Use Case Template",
    description="Learning Activity Dashboard API",
    version="1.0.0"
)

# CORS setup for frontend communication
origins = ["http://localhost:3000", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup stub for Microsoft Entra ID/Azure AD
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    scopes={"openid": "OpenID Connect scope"}
)

# --- Role-Based Access Control ---
class UserRole(str, enum.Enum):
    learning_coordinator = "Learning Program Coordinator"
    employee = "Employee"
    trainer = "Trainer/Mentor"
    manager = "Manager"
    administrator = "Administrator"

# --- Models ---
class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

class TrainingProgram(BaseModel):
    id: int
    title: str
    description: Optional[str]
    active: bool

class Session(BaseModel):
    id: int
    program_id: int
    title: str
    capacity: int
    registered_count: int = 0
    start_time: str
    end_time: str

class ProgressStatus(str, enum.Enum):
    not_started = "Not Started"
    in_progress = "In Progress"
    completed = "Completed"

class CourseProgress(BaseModel):
    program_id: int
    status: ProgressStatus
    completion_percentage: float

class Feedback(BaseModel):
    session_id: int
    user_id: int
    rating: int  # Rating 1-5
    comments: Optional[str]

class AttendanceRecord(BaseModel):
    session_id: int
    user_id: int
    attended: bool

# Simulated in-memory data storage (mocked for demo)
users_db = [
    {"id": 1, "name": "Alice Employee", "email": "alice@example.com", "role": UserRole.employee},
    {"id": 2, "name": "Bob Trainer", "email": "bob@example.com", "role": UserRole.trainer},
    {"id": 3, "name": "Chris Manager", "email": "chris@example.com", "role": UserRole.manager},
    {"id": 4, "name": "Diana Admin", "email": "diana@example.com", "role": UserRole.administrator}
]

training_programs_db = [
    {"id": 1, "title": "Data Security Basics", "description": "Intro to data security", "active": True},
    {"id": 2, "title": "Advanced Power BI", "description": "Power BI analytics training", "active": True}
]

sessions_db = [
    {"id": 1, "program_id": 1, "title": "Session 1", "capacity": 3, "registered_count": 1, "start_time": "2024-07-01T10:00:00Z", "end_time": "2024-07-01T12:00:00Z"},
    {"id": 2, "program_id": 2, "title": "Session 1", "capacity": 2, "registered_count": 0, "start_time": "2024-07-05T14:00:00Z", "end_time": "2024-07-05T16:00:00Z"}
]

registrations_db = [
    {"session_id": 1, "user_id": 1},
]

progress_db = [
    {"program_id": 1, "user_id": 1, "status": ProgressStatus.in_progress, "completion_percentage": 50.0},
    {"program_id": 2, "user_id": 1, "status": ProgressStatus.not_started, "completion_percentage": 0.0}
]

feedback_db = []

attendance_db = []

# --- Auth and RBAC dependencies ---
from fastapi import Security

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    # NOTE: This is a stub. Replace with real OpenID Connect token parsing and user lookup.
    # For demo, we return first user as logged-in employee for AC001
    # In real app, decode token and get user details and roles
    demo_user = users_db[0]
    return UserBase(**demo_user)

def require_roles(*roles: UserRole):
    def role_checker(current_user: UserBase = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions."
            )
        return current_user
    return role_checker

# --- API Endpoints ---

@app.get("/dashboard/employee", response_model=List[CourseProgress])
async def get_employee_dashboard(
    current_user: UserBase = Depends(require_roles(UserRole.employee))
):
    # AC001: Return assigned training programs and current completion status
    user_progress = [
        CourseProgress(
            program_id=prog["program_id"],
            status=prog["status"],
            completion_percentage=prog["completion_percentage"]
        )
        for prog in progress_db if prog["user_id"] == current_user.id
    ]
    return user_progress

class FeedbackRequest(BaseModel):
    session_id: int
    rating: int
    comments: Optional[constr(strip_whitespace=True, min_length=0)] = None

@app.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_request: FeedbackRequest,
    current_user: UserBase = Depends(require_roles(UserRole.employee))
):
    # Validate required feedback fields: rating 1-5
    if feedback_request.rating < 1 or feedback_request.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rating must be an integer between 1 and 5."
        )
    # AC002 Save feedback and reflect in reports (mocked here by adding to list)
    feedback_db.append({
        "session_id": feedback_request.session_id,
        "user_id": current_user.id,
        "rating": feedback_request.rating,
        "comments": feedback_request.comments
    })
    return {"message": "Feedback submitted successfully."}

@app.post("/sessions/{session_id}/attendance", status_code=status.HTTP_200_OK)
async def mark_attendance(
    session_id: int,
    user_id: int,
    current_user: UserBase = Depends(require_roles(UserRole.trainer, UserRole.administrator))
):
    # AC003 Update attendance
    # Validate session exists
    session = next((s for s in sessions_db if s["id"] == session_id), None)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    # Save attendance
    attendance_db.append({"session_id": session_id, "user_id": user_id, "attended": True})
    return {"message": "Attendance recorded."}

class TeamAnalytics(BaseModel):
    attendance_rate: float
    completion_rate: float
    feedback_trend: float

@app.get("/dashboard/manager/analytics", response_model=TeamAnalytics)
async def get_manager_team_analytics(
    current_user: UserBase = Depends(require_roles(UserRole.manager))
):
    # AC004 Provide team attendance, completion, feedback trend mocked
    # For demo, return fixed values
    return TeamAnalytics(attendance_rate=90.0, completion_rate=85.0, feedback_trend=4.2)

@app.get("/admin/features")
async def admin_features(
    current_user: UserBase = Depends(require_roles(UserRole.administrator))
):
    # R006 Admin can access management and reports
    return {"message": "Welcome Administrator. Manage users, programs, reports here."}

@app.get("/admin/forbidden")
async def admin_forbidden_route(
    current_user: UserBase = Depends(get_current_user)
):
    # Unauthorized access demonstration
    if current_user.role != UserRole.administrator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions."
        )
    return {"message": "Sensitive admin feature."}

# Error handlers for common errors
from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/")
async def root():
    return {"message": "Autoforge Use Case Template API is running."}

# Serve the packaged UI at / while preserving API routes and static assets.
from fastapi.responses import FileResponse as _AutoForgeFileResponse
from fastapi.staticfiles import StaticFiles as _AutoForgeStaticFiles
@app.middleware("http")
async def _autoforge_serve_frontend_root(request, call_next):
    if request.method == "GET" and request.url.path == "/":
        return _AutoForgeFileResponse("/app/frontend/build/index.html")
    return await call_next(request)
app.mount("/", _AutoForgeStaticFiles(directory="/app/frontend/build", html=True), name="frontend")
