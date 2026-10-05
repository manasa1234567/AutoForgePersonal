from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .schemas import ApplicationCreate, Application
from . import crud, models
from .database import SessionLocal, engine, Base

import os

app = FastAPI(title="Application Form API with Persistence")

Base.metadata.create_all(bind=engine)

# Allow CORS for local frontend development and deployment flexible origin
frontend_origin = os.getenv('FRONTEND_ORIGIN', 'http://localhost:3000')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Application Form API is running."}

@app.post("/submit", status_code=201, response_model=Application)
def submit_application(form: ApplicationCreate, db: Session = Depends(get_db)):
    # Create application record in DB
    try:
        application = crud.create_application(db, form)
        return application
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
