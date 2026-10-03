from io import BytesIO
import re
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from ..models.schemas import ApprovalRequest, BlueprintUpdate, BuildCreate, BuildState, RefineRequest
from ..services.orchestrator import Orchestrator

router = APIRouter(prefix="/api/builds", tags=["builds"])
store = Orchestrator()


@router.post("", status_code=201)
async def create_build(payload: BuildCreate):
    try:
        return store.create(payload)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("")
async def list_builds() -> list[BuildState]:
    return store.list()


@router.post("/{build_id}/start")
async def start_build(build_id: str):
    try:
        return await store.start(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{build_id}")
async def get_build(build_id: str):
    try:
        return store.get(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{build_id}/events")
async def get_events(build_id: str):
    try:
        return store.get(build_id).audit
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{build_id}/artifacts.zip")
async def download_artifacts(build_id: str):
    try:
        build = store.get(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Build not found") from exc
    artifacts = build.proof.artifacts if build.proof else {}
    if not artifacts:
        raise HTTPException(status_code=404, detail="Generated artifacts are not available yet")

    archive = BytesIO()
    with zipfile.ZipFile(archive, mode="w", compression=zipfile.ZIP_DEFLATED) as zipped:
        for path, content in artifacts.items():
            normalized = path.replace("\\", "/")
            if (
                normalized.startswith("/")
                or re.match(r"^[A-Za-z]:", normalized)
                or any(part in {"", ".", ".."} for part in normalized.split("/"))
            ):
                continue
            zipped.writestr(normalized, content)
    archive.seek(0)
    safe_title = re.sub(r"[^A-Za-z0-9_-]+", "-", build.title).strip("-")[:60] or "autoforge-project"
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}-{build.id}.zip"'},
    )


@router.get("/{build_id}/preview", response_class=HTMLResponse)
async def preview_artifacts(build_id: str):
    try:
        build = store.get(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Build not found") from exc
    artifacts = build.proof.artifacts if build.proof else {}
    preview = artifacts.get("preview/index.html")
    if not preview:
        raise HTTPException(status_code=404, detail="A static UI preview was not generated for this build")
    return HTMLResponse(
        preview,
        headers={
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:; form-action 'none'; base-uri 'none'; frame-ancestors 'self'",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Cache-Control": "no-store",
        },
    )


@router.post("/{build_id}/approve")
async def approve_build(build_id: str, payload: ApprovalRequest):
    try:
        return await store.approve(build_id, payload.gate)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.put("/{build_id}/blueprint")
async def update_blueprint(build_id: str, payload: BlueprintUpdate):
    try:
        return store.update_blueprint(build_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{build_id}/refine")
async def refine_build(build_id: str, payload: RefineRequest):
    try:
        return await store.refine(build_id, payload.text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{build_id}/artifacts/refine")
async def refine_artifacts(build_id: str, payload: RefineRequest):
    try:
        return await store.refine_artifacts(build_id, payload.text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Build not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{build_id}/security-review")
async def review_build_security(build_id: str):
    try:
        await store.run_security_review(build_id)
        return store.get(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{build_id}/deployment-preflight")
async def prepare_build_deployment(build_id: str):
    try:
        await store.prepare_deployment(build_id)
        return store.get(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
