from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, coordinator, employee, trainer, manager, admin, dashboard

app = FastAPI(title="Learning Management System API", version="1.0.0")

# CORS middleware for frontend integration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(coordinator.router, prefix="/coordinator", tags=["Coordinator"])
app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(trainer.router, prefix="/trainer", tags=["Trainer"])
app.include_router(manager.router, prefix="/manager", tags=["Manager"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {"message": "Learning Management System API is running"}

# Serve the packaged UI at / while preserving API routes and static assets.
from fastapi.responses import FileResponse as _AutoForgeFileResponse
from fastapi.staticfiles import StaticFiles as _AutoForgeStaticFiles
@app.middleware("http")
async def _autoforge_serve_frontend_root(request, call_next):
    if request.method == "GET" and request.url.path == "/":
        return _AutoForgeFileResponse("/app/frontend/build/index.html")
    return await call_next(request)
app.mount("/", _AutoForgeStaticFiles(directory="/app/frontend/build", html=True), name="frontend")
