from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import application

app = FastAPI(title="Application Form API", version="1.0.0")

# CORS for dev, allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(application.router, prefix="/application", tags=["application"])

@app.get("/", summary="Health Check")
async def root():
    return {"status": "ok"}
