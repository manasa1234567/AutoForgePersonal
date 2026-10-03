import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.agents import router as agents_router
from .routers.builds import router as builds_router
from .routers.skills import router as skills_router
from .routers.integrations import router as integrations_router

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
app.include_router(skills_router)
app.include_router(integrations_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    foundry_requested = bool(os.getenv("FOUNDRY_PROJECT_ENDPOINT"))
    foundry_model = os.getenv("FOUNDRY_SPEC_MODEL") or os.getenv("FOUNDRY_MODEL")
    foundry_configured = foundry_requested and bool(foundry_model)
    openai_requested = any(
        os.getenv(name)
        for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")
    )
    azure_openai_configured = all(
        os.getenv(name)
        for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")
    )
    cloud_model_requested = foundry_requested or openai_requested
    cloud_model_configured = foundry_configured if foundry_requested else azure_openai_configured
    prompt_shields_configured = bool(os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT"))
    if foundry_requested:
        mode = "foundry" if foundry_configured else "misconfigured"
    elif azure_openai_configured:
        mode = "azure-openai"
    elif cloud_model_requested:
        mode = "misconfigured"
    else:
        mode = "deterministic-demo"
    return {
        "status": "ok",
        "mode": mode,
        "persistence": "azure" if os.getenv("AUTOFORGE_PERSISTENCE", "local").strip().lower() == "azure" else "local",
        "service": "aegis-autoforge",
        "spec_agent": "configured" if cloud_model_configured else "misconfigured" if cloud_model_requested else "demo",
        "prompt_shields": "configured" if prompt_shields_configured else "missing" if cloud_model_requested else "local-marker-check",
        "agent1_cloud_ready": str(cloud_model_configured and prompt_shields_configured).lower(),
    }
