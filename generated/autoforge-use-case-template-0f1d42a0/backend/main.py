import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import databases
import sqlalchemy
from typing import List
from pydantic import BaseModel
import logging

# Database config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/autoforge")

import asyncio
import sqlalchemy.ext.asyncio

metadata = sqlalchemy.MetaData()


# SQLAlchemy table definitions
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text
from sqlalchemy.sql import func

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("name", String, nullable=False),
    Column("role", String, nullable=False),  # Roles: employee, trainer, manager, admin
)

programs = Table(
    "programs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", Text, nullable=True),
    Column("active", Boolean, default=True),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("program_id", Integer, ForeignKey("programs.id")),
    Column("title", String, nullable=False),
    Column("scheduled_at", DateTime, nullable=False),
    Column("capacity", Integer, nullable=False, default=0),
)

registrations = Table(
    "registrations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", Integer, ForeignKey("sessions.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("attendance", Boolean, default=False),
    Column("completed", Boolean, default=False),
    Column("feedback_submitted", Boolean, default=False),
)

feedbacks = Table(
    "feedbacks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("registration_id", Integer, ForeignKey("registrations.id")),
    Column("rating", Integer),
    Column("comments", Text),
)

certificates = Table(
    "certificates",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("program_id", Integer, ForeignKey("programs.id")),
    Column("generated_at", DateTime, server_default=func.now()),
    Column("certificate_url", String),
)


# Async engine and database
engine = sqlalchemy.ext.asyncio.create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)
database = databases.Database(DATABASE_URL)

app = FastAPI(title="AutoForge Training Dashboard Backend")

# CORS for frontend during development (Allow localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Mount frontend static files at root
app.mount("/", StaticFiles(directory="./static", html=True), name="static")

# Roles allowed
ROLES = ["employee", "trainer", "manager", "admin"]

# --- Authentication & Authorization ---

# Using OAuth2AuthorizationCodeBearer for Azure AD
# Placeholder config for Azure AD
TENANT_ID = os.getenv("AZURE_TENANT_ID", "your-tenant-id")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "your-client-id")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "your-client-secret")

OAUTH2_SCHEME = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize",
    tokenUrl=f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
    scopes={"openid": "OpenID Connect scope"}
)

# Dummy verify token function
async def get_current_user(token: str = Depends(OAUTH2_SCHEME)) -> dict:
    # TODO: Verify token with Azure AD
    # For demo, parse token as user email
    # In real app, verify token signature and claims
    user_email = token  # not real
    query = users.select().where(users.c.email == user_email)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return dict(user)

# RBAC check
def role_required(allowed_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return current_user
    return role_checker

@app.on_event("startup")
async def startup():
    await database.connect()
    # Create tables if not existing - for demo only (not production)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- API Models ---

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str

class ProgramOut(BaseModel):
    id: int
    title: str
    description: str | None
    active: bool

class SessionOut(BaseModel):
    id: int
    program_id: int
    title: str
    scheduled_at: str
    capacity: int

class RegistrationOut(BaseModel):
    id: int
    session_id: int
    user_id: int
    attendance: bool
    completed: bool
    feedback_submitted: bool

class FeedbackCreate(BaseModel):
    registration_id: int
    rating: int # Eg. 1-5
    comments: str | None

class FeedbackOut(BaseModel):
    id: int
    registration_id: int
    rating: int
    comments: str | None

class CertificateOut(BaseModel):
    id: int
    user_id: int
    program_id: int
    generated_at: str
    certificate_url: str

# --- API Endpoints ---

@app.get("/api/user/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/api/programs", response_model=List[ProgramOut])
async def list_programs(current_user: dict = Depends(get_current_user)):
    # All active programs
    query = programs.select().where(programs.c.active == True)
    results = await database.fetch_all(query)
    return results

@app.get("/api/user/{user_id}/assigned-programs", response_model=List[ProgramOut])
async def get_user_assigned_programs(user_id: int, current_user: dict = Depends(get_current_user)):
    # For employee: show programs linked via sessions and registrations
    # Simplified: programs where user has any registration
    query = (
        sqlalchemy.select(programs)
        .join(sessions, sessions.c.program_id == programs.c.id)
        .join(registrations, registrations.c.session_id == sessions.c.id)
        .where(registrations.c.user_id == user_id)
        .where(programs.c.active == True)
        .distinct()
    )
    results = await database.fetch_all(query)
    return results

@app.get("/api/user/{user_id}/programs/{program_id}/sessions", response_model=List[SessionOut])
async def get_program_sessions(user_id: int, program_id: int, current_user: dict = Depends(get_current_user)):
    # List sessions for this program where user is registered
    query = (
        sqlalchemy.select(sessions)
        .join(registrations, registrations.c.session_id == sessions.c.id)
        .where(sessions.c.program_id == program_id)
        .where(registrations.c.user_id == user_id)
    )
    results = await database.fetch_all(query)
    return results

@app.post("/api/feedback", status_code=201)
async def submit_feedback(feedback: FeedbackCreate, current_user: dict = Depends(role_required(["employee"]))):
    # Check registration exists and belongs to user
    query_reg = registrations.select().where(registrations.c.id == feedback.registration_id)
    reg = await database.fetch_one(query_reg)
    if not reg or reg.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Registration not found or access denied")

    # Check session completion
    if not reg.completed:
        raise HTTPException(status_code=400, detail="Cannot submit feedback before completion")

    # Validate rating
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # Insert feedback
    query_insert = feedbacks.insert().values(
        registration_id=feedback.registration_id,
        rating=feedback.rating,
        comments=feedback.comments
    )
    feedback_id = await database.execute(query_insert)

    # Update registration feedback_submitted
    query_update = (
        registrations.update()
        .where(registrations.c.id == feedback.registration_id)
        .values(feedback_submitted=True)
    )
    await database.execute(query_update)

    return {"message": "Feedback submitted successfully", "id": feedback_id}

@app.get("/api/user/{user_id}/registrations", response_model=List[RegistrationOut])
async def get_registrations_for_user(user_id: int, current_user: dict = Depends(get_current_user)):
    # Only user themselves or higher roles
    if current_user["id"] != user_id and current_user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    query = registrations.select().where(registrations.c.user_id == user_id)
    results = await database.fetch_all(query)
    return results

@app.get("/api/session/{session_id}/participants", response_model=List[UserOut])
async def get_session_participants(session_id: int, current_user: dict = Depends(role_required(["trainer", "admin"]))):
    # List users registered for a session
    query = (
        sqlalchemy.select(users)
        .join(registrations, registrations.c.user_id == users.c.id)
        .where(registrations.c.session_id == session_id)
    )
    results = await database.fetch_all(query)
    return results

@app.post("/api/session/{session_id}/mark-attendance")
async def mark_attendance(session_id: int, user_id: int, attended: bool, current_user: dict = Depends(role_required(["trainer", "admin"]))):
    # Mark attendance for user in session
    query = (
        registrations.update()
        .where(registrations.c.session_id == session_id)
        .where(registrations.c.user_id == user_id)
        .values(attendance=attended)
    )
    result = await database.execute(query)
    if result == 0:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"message": "Attendance updated"}

@app.get("/api/manager/team-progress", response_model=dict)
async def get_team_progress(current_user: dict = Depends(role_required(["manager", "admin"]))):
    # Placeholder: aggregate attendance, completion, feedback stats for manager's team
    # Here returns dummy data
    return {
        "attendance_rate": 0.75,
        "completion_rate": 0.60,
        "feedback_average": 4.3
    }

@app.get("/api/admin/users", response_model=List[UserOut])
async def list_users(current_user: dict = Depends(role_required(["admin"]))):
    query = users.select()
    results = await database.fetch_all(query)
    return results

@app.post("/api/admin/users", status_code=201)
async def create_user(user: UserOut, current_user: dict = Depends(role_required(["admin"]))):
    query = users.insert().values(
        email=user.email, name=user.name, role=user.role
    )
    user_id = await database.execute(query)
    return {"id": user_id}

@app.delete("/api/admin/users/{user_id}", status_code=204)
async def delete_user(user_id: int, current_user: dict = Depends(role_required(["admin"]))):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return JSONResponse(status_code=204, content=None)

# --- Health and fallback ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Custom exception for 403
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": "Access Denied - You do not have permission to view this resource."}
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
