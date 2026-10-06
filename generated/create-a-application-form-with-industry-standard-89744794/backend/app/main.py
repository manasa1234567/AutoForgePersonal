from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr
from typing import Optional

app = FastAPI(title="Application Form API")

# Enable CORS for local development frontend (React running on 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for incoming application form data
class ApplicationForm(BaseModel):
    first_name: constr(min_length=1)
    last_name: constr(min_length=1)
    email: EmailStr
    phone: constr(min_length=7, max_length=15)
    address_line1: constr(min_length=1)
    address_line2: Optional[constr(max_length=100)] = None
    city: constr(min_length=1)
    state: constr(min_length=1)
    zip_code: constr(min_length=3, max_length=10)
    country: constr(min_length=1)
    date_of_birth: constr(min_length=10, max_length=10)  # YYYY-MM-DD
    position_applied: constr(min_length=1)
    cover_letter: Optional[constr(max_length=2000)] = None

@app.get("/")
async def root():
    return {"message": "Application Form API is running."}

@app.post("/submit")
async def submit_application(form: ApplicationForm):
    # In real scenario: Save data to the PostgreSQL database
    # Here we simulate successful submission
    # Validate date_of_birth format further could be done here if needed
    if len(form.date_of_birth) != 10 or form.date_of_birth[4] != '-' or form.date_of_birth[7] != '-':
        raise HTTPException(status_code=400, detail="date_of_birth must be in YYYY-MM-DD format")
    # Simulate acceptance
    return {"message": "Application submitted successfully.", "data": form.dict()}

# Serve the packaged UI at / while preserving API routes and static assets.
from fastapi.responses import FileResponse as _AutoForgeFileResponse
from fastapi.staticfiles import StaticFiles as _AutoForgeStaticFiles
@app.middleware("http")
async def _autoforge_serve_frontend_root(request, call_next):
    if request.method == "GET" and request.url.path == "/":
        return _AutoForgeFileResponse("/app/app/static/index.html")
    return await call_next(request)
app.mount("/", _AutoForgeStaticFiles(directory="/app/app/static", html=True), name="frontend")
