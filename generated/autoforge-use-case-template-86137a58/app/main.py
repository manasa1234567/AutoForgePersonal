from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app import models, services, auth

app = FastAPI(
    title="Learning Dashboard API",
    description="REST API for centralized learning dashboard with role-based access",
    version="1.0.0"
)

# CORS middleware for frontend access
# Restrict origins to the frontend application URL for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # Adjust to frontend deployment URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for OAuth2 token (using Microsoft Entra ID / Azure AD)
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token",
    scopes={"User.Read":"Read user profile"},
)

# Roles for RBAC
ROLE_EMPLOYEE = "Employee"
ROLE_TRAINER = "Trainer/Mentor"
ROLE_MANAGER = "Manager"
ROLE_COORDINATOR = "Learning Program Coordinator"
ROLE_ADMIN = "Administrator"


# Auth dependency extracting user info and roles
async def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
    user = await auth.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@app.get("/dashboard", response_model=models.DashboardData)
async def get_dashboard(current_user: models.User = Depends(get_current_user)):
    # Role-based dispatch
    if ROLE_EMPLOYEE in current_user.roles:
        return await services.employee_dashboard(current_user)
    elif ROLE_TRAINER in current_user.roles:
        return await services.trainer_dashboard(current_user)
    elif ROLE_MANAGER in current_user.roles:
        return await services.manager_dashboard(current_user)
    elif ROLE_COORDINATOR in current_user.roles:
        return await services.coordinator_dashboard(current_user)
    elif ROLE_ADMIN in current_user.roles:
        return await services.admin_dashboard(current_user)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions",
        )


@app.get("/programs/assigned", response_model=List[models.AssignedProgram])
async def get_assigned_programs(current_user: models.User = Depends(get_current_user)):
    if ROLE_EMPLOYEE not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return await services.get_employee_assigned_programs(current_user.id)


@app.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: models.FeedbackCreate, current_user: models.User = Depends(get_current_user)):
    if ROLE_EMPLOYEE not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    # Validate feedback internally in Pydantic
    saved = await services.save_feedback(current_user.id, feedback)
    if not saved:
        raise HTTPException(status_code=400, detail="Failed to save feedback")
    return {"message": "Feedback submitted successfully"}


@app.post("/attendance/mark", status_code=status.HTTP_200_OK)
async def mark_attendance(attendance: models.AttendanceMark, current_user: models.User = Depends(get_current_user)):
    if ROLE_TRAINER not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    success = await services.mark_attendance(current_user.id, attendance)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to mark attendance")
    return {"message": "Attendance marked successfully"}


@app.get("/team/analytics", response_model=models.TeamAnalytics)
async def get_team_analytics(current_user: models.User = Depends(get_current_user)):
    if ROLE_MANAGER not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return await services.manager_team_analytics(current_user.id)


@app.get("/admin/users", response_model=List[models.UserSummary])
async def admin_users(current_user: models.User = Depends(get_current_user)):
    if ROLE_ADMIN not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return await services.admin_list_users()


@app.get("/admin/programs", response_model=List[models.ProgramSummary])
async def admin_programs(current_user: models.User = Depends(get_current_user)):
    if ROLE_ADMIN not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return await services.admin_list_programs()


@app.post("/admin/users", status_code=status.HTTP_201_CREATED)
async def admin_create_user(user_create: models.UserCreate, current_user: models.User = Depends(get_current_user)):
    if ROLE_ADMIN not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    user = await services.admin_create_user(user_create)
    return user


@app.get("/openapi.json")
def get_openapi():
    return app.openapi()

# Serve the packaged UI at / while preserving API routes and static assets.
from fastapi.responses import FileResponse as _AutoForgeFileResponse
from fastapi.staticfiles import StaticFiles as _AutoForgeStaticFiles
@app.middleware("http")
async def _autoforge_serve_frontend_root(request, call_next):
    if request.method == "GET" and request.url.path == "/":
        return _AutoForgeFileResponse("/app/frontend/build/index.html")
    return await call_next(request)
app.mount("/", _AutoForgeStaticFiles(directory="/app/frontend/build", html=True), name="frontend")
