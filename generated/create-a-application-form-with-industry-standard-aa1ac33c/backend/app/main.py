from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
import uvicorn
import os

app = FastAPI(title="Application Form Backend")

# Configure CORS origins from environment variable or default to empty list
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # No origins allowed if environment variable not set
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class ApplicationData(BaseModel):
    firstName: constr(strip_whitespace=True, min_length=1)
    lastName: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone: constr(strip_whitespace=True, min_length=7)
    dateOfBirth: constr(strip_whitespace=True, min_length=1)
    gender: constr(strip_whitespace=True, min_length=1)
    address: constr(strip_whitespace=True, min_length=1)
    city: constr(strip_whitespace=True, min_length=1)
    state: constr(strip_whitespace=True, min_length=1)
    postalCode: constr(strip_whitespace=True, min_length=1)
    country: constr(strip_whitespace=True, min_length=1)
    position: constr(strip_whitespace=True, min_length=1)
    expectedSalary: float
    startDate: constr(strip_whitespace=True, min_length=1)
    coverLetter: Optional[constr(strip_whitespace=True)] = None
    agreeToTerms: bool


@app.post("/api/applications")
async def receive_application(
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    dateOfBirth: str = Form(...),
    gender: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    postalCode: str = Form(...),
    country: str = Form(...),
    position: str = Form(...),
    expectedSalary: float = Form(...),
    startDate: str = Form(...),
    coverLetter: Optional[str] = Form(None),
    agreeToTerms: bool = Form(...),
    resume: UploadFile = File(...),
):
    if not agreeToTerms:
        raise HTTPException(status_code=400, detail="Terms must be agreed to.")

    try:
        app_data = ApplicationData(
            firstName=firstName,
            lastName=lastName,
            email=email,
            phone=phone,
            dateOfBirth=dateOfBirth,
            gender=gender,
            address=address,
            city=city,
            state=state,
            postalCode=postalCode,
            country=country,
            position=position,
            expectedSalary=expectedSalary,
            startDate=startDate,
            coverLetter=coverLetter,
            agreeToTerms=agreeToTerms,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    allowed_mime_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    if resume.content_type not in allowed_mime_types:
        raise HTTPException(status_code=400, detail="Invalid resume file type.")

    return JSONResponse(content={"message": "Application received successfully."}, status_code=201)


@app.get("/")
async def root():
    return {"message": "Application Form Backend Running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
