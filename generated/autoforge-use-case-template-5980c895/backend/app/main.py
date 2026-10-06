from fastapi import FastAPI
from starlette.responses import RedirectResponse
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.db import init_db
from app.core.logger import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# CORS middleware - allow frontend localhost and same origin, can be expanded if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.on_event("startup")
async def startup_event():
    # Initialize DB and other startup tasks
    try:
        await init_db()
        logger.info("Startup completed: database connected.")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
