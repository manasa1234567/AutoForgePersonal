from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.agents import router as agents_router
from .routers.builds import router as builds_router

app = FastAPI(title="AegisAI AutoForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(builds_router)
app.include_router(agents_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": "mock", "service": "aegis-autoforge"}
