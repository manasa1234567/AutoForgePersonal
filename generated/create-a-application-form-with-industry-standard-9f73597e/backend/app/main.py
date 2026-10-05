from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

DATABASE_URL = os.getenv('DATABASE_URL', '')

app = FastAPI(title="Application Form API")

Base = declarative_base()

class ApplicationSubmission(Base):
    __tablename__ = 'application_submissions'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=False)  # ISO date string YYYY-MM-DD
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state_province = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    education_level = Column(String, nullable=False)
    employment_status = Column(String, nullable=False)
    resume_text = Column(Text, nullable=True)
    agree_to_terms = Column(Boolean, nullable=False)

class ApplicationForm(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    phone: Optional[constr(strip_whitespace=True, min_length=7, max_length=15)] = None
    date_of_birth: constr(regex=r"^\d{4}-\d{2}-\d{2}$")  # ISO date string YYYY-MM-DD
    address_line1: constr(strip_whitespace=True, min_length=1)
    address_line2: Optional[constr(strip_whitespace=True)] = None
    city: constr(strip_whitespace=True, min_length=1)
    state_province: constr(strip_whitespace=True, min_length=1)
    postal_code: constr(strip_whitespace=True, min_length=1)
    country: constr(strip_whitespace=True, min_length=1)
    education_level: constr(strip_whitespace=True, min_length=1)
    employment_status: constr(strip_whitespace=True, min_length=1)
    resume_text: Optional[constr(strip_whitespace=True)] = None
    agree_to_terms: bool

# Set up DB session
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
else:
    engine = None
    SessionLocal = None

# Dependency
def get_db():
    if not SessionLocal:
        raise HTTPException(status_code=503, detail="Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Application Form API is running."}

@app.post("/submit")
async def submit_application(form: ApplicationForm, db: Session = Depends(get_db)):
    if not form.agree_to_terms:
        raise HTTPException(status_code=400, detail="Terms agreement is required.")
    # Save to DB
    submission = ApplicationSubmission(
        first_name=form.first_name,
        last_name=form.last_name,
        email=form.email,
        phone=form.phone,
        date_of_birth=form.date_of_birth,
        address_line1=form.address_line1,
        address_line2=form.address_line2,
        city=form.city,
        state_province=form.state_province,
        postal_code=form.postal_code,
        country=form.country,
        education_level=form.education_level,
        employment_status=form.employment_status,
        resume_text=form.resume_text,
        agree_to_terms=form.agree_to_terms
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {"message": "Application submitted successfully.", "id": submission.id}
