from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Application Form API")


class ApplicationData(BaseModel):
    firstName: constr(strip_whitespace=True, max_length=50)
    lastName: constr(strip_whitespace=True, max_length=50)
    email: EmailStr
    phone: constr(strip_whitespace=True, min_length=7, max_length=15, pattern=r'^\+?\d{7,15}$')
    dateOfBirth: constr(strip_whitespace=True, min_length=10, max_length=10)  # yyyy-mm-dd
    address: constr(strip_whitespace=True, max_length=100)
    city: constr(strip_whitespace=True, max_length=50)
    state: constr(strip_whitespace=True, max_length=50)
    zipCode: constr(strip_whitespace=True, max_length=20)
    country: constr(strip_whitespace=True, max_length=50)
    gender: constr(strip_whitespace=True, max_length=20)
    educationLevel: constr(strip_whitespace=True, max_length=50)
    resumeText: constr(strip_whitespace=True, max_length=5000)
    agreeTerms: bool


# Restrict CORS origins to allow only frontend origin for security (example localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Application Form API is running."}


@app.post("/api/applications", status_code=201)
async def submit_application(data: ApplicationData):
    # Verify agreeTerms
    if not data.agreeTerms:
        raise HTTPException(status_code=400, detail="You must agree to the terms and conditions.")

    # For demo purpose, we just accept and return success
    return {"message": "Application submitted successfully"}
