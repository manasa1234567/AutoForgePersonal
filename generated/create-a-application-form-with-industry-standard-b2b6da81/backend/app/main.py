from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Application Form API", version="1.0.0")

# For now, CORS middleware to allow frontend localhost dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Application Form API is running."}

# A stub endpoint for form submission
from fastapi import UploadFile, File, Form, HTTPException
from typing import Optional

@app.post("/submit-application")
async def submit_application(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    country: str = Form(...),
    date_of_birth: str = Form(...),
    gender: Optional[str] = Form(None),
    consent: bool = Form(...),
    resume: Optional[UploadFile] = File(None),
):
    # Basic validation
    if not consent:
        raise HTTPException(status_code=400, detail="Consent required")
    # Here you'd typically insert into DB and persist uploaded file if present
    # For demo return success
    return {"detail": "Application submitted successfully"}
