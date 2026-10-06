import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from .routers import dashboard, users, auth, programs, sessions, feedback, attendance, admin
from .core.auth import get_current_active_user
from .core.logger import logger

app = FastAPI(title="Enterprise Learning Management System")

# CORS - allow frontend on localhost:3000 and later adjust
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(programs.router, prefix="/programs", tags=["programs"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status_code={response.status_code}")
    return response

@app.get("/")
async def root():
    return {"message": "Enterprise Learning Management System API is running."}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})

@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc):
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    return JSONResponse(status_code=403, content={"detail": "Access denied"})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
