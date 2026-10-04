from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Simple token OAuth2 mock (for demonstration only)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)

class PageCreateResponse(BaseModel):
    message: str

app = FastAPI(title="Hi Page Creator API")

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Placeholder function to simulate user authentication
# In real usage, validate tokens and permissions here
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "valid-token":
        # Unauthorized
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return {"username": "authorized_user"}

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.post("/pages/hi", response_model=PageCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_hi_page(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_page = db.query(Page).filter(Page.title == "hi").first()
    if existing_page:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The 'hi' page already exists."
        )
    new_page = Page(title="hi")
    db.add(new_page)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the page due to an internal error."
        )
    return {"message": "The 'hi' page was created successfully."}

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok"}
