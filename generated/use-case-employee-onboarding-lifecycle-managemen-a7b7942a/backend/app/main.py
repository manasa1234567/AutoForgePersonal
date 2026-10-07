from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import employee_router, auth_router, onboarding_router, document_router, equipment_router, leave_router, ai_assistant_router

app = FastAPI(title="Employee Onboarding & Lifecycle Management Portal API",
              description="API for managing employee onboarding, lifecycle, documents, equipment, leave, and AI assistant interactions.",
              version="1.0.0")

# CORS: Allow frontend running on localhost or deployed domain
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add production domain here if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(employee_router.router, prefix="/employees", tags=["employees"])
app.include_router(onboarding_router.router, prefix="/onboarding", tags=["onboarding"])
app.include_router(document_router.router, prefix="/documents", tags=["documents"])
app.include_router(equipment_router.router, prefix="/equipment", tags=["equipment"])
app.include_router(leave_router.router, prefix="/leave", tags=["leave"])
app.include_router(ai_assistant_router.router, prefix="/ai", tags=["ai-assistant"])

@app.get("/")
def root():
    return {"message": "Employee Onboarding & Lifecycle Management Portal API is running."}

# Serve the packaged UI at / while preserving API routes and static assets.
from fastapi.responses import FileResponse as _AutoForgeFileResponse
from fastapi.staticfiles import StaticFiles as _AutoForgeStaticFiles
@app.middleware("http")
async def _autoforge_serve_frontend_root(request, call_next):
    if request.method == "GET" and request.url.path == "/":
        return _AutoForgeFileResponse("/app/backend/static/index.html")
    return await call_next(request)
app.mount("/", _AutoForgeStaticFiles(directory="/app/backend/static", html=True), name="frontend")
