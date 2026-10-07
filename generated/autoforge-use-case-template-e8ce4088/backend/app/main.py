from fastapi import FastAPI
from .api import api_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import os

app = FastAPI(title="AutoForge Use Case Template Backend", version="0.1.0")

# Mount frontend static files
app.mount("/", StaticFiles(directory="./static", html=True), name="static")

# Include API routes
app.include_router(api_router)

# Environment variable to define allowed origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000").split(",")

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optionally enable HTTPS redirect in production (comment out if using reverse proxy handling TLS)
# app.add_middleware(HTTPSRedirectMiddleware)
