from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router

app = FastAPI(
    title="AutoForge Use Case Template",
    description="A FastAPI backend for employee learning management",
    version="1.0.0"
)

# CORS middleware for frontend integration, can be tuned per deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router,prefix="/api")

@app.get("/", tags=["Root"])
async def root():
    return {"message": "AutoForge Use Case Template Backend is running."}
