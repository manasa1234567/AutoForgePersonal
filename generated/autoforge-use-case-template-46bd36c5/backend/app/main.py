from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, dashboard, feedback, sessions
from app.services.feedback_service import FeedbackService
from app.services.sessions_service import SessionsService
from app.services.users_service import UsersService
from fastapi import Depends

app = FastAPI(title="Autoforge Learning Dashboard Backend")

# Dependency Injection


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}

# Adding CORS middleware for frontend connection
# Restrict origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Common local dev origins for React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(feedback.router)
app.include_router(sessions.router)

# Dependency Providers
@app.dependency()
def get_feedback_service() -> FeedbackService:
    return FeedbackService()

@app.dependency()
def get_sessions_service() -> SessionsService:
    return SessionsService()

@app.dependency()
def get_users_service() -> UsersService:
    return UsersService()

# Attach dependencies to router dependencies where needed
feedback.router.dependencies.append(Depends(get_feedback_service))
sessions.router.dependencies.extend([Depends(get_sessions_service)])
users.router.dependencies.append(Depends(get_users_service))
