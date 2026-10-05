from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr
from typing import Optional

app = FastAPI(title="Application Form API")

class ApplicationData(BaseModel):
    first_name: constr(min_length=1)
    last_name: constr(min_length=1)
    email: EmailStr
    phone: Optional[constr(min_length=10, max_length=15)] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Application Form API is running."}

@app.post("/submit")
async def submit_application(data: ApplicationData):
    # In a real app, here would be saving to DB etc.
    # We simulate success response
    return {"message": "Application submitted successfully", "data": data.dict()}
