import hmac
import os
import re
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from ..models.schemas import ApprovalRequest, BlueprintUpdate, BuildCreate, BuildState, DeploymentCallback, RefineRequest
from ..services.orchestrator import Orchestrator
from ..services.ui_preview import PreviewService, PreviewError, preview_artifacts, preview_viewer, PREVIEW_CSP, VIEWER_CSP
from ..services.preview_archive import preview_zip, safe_artifacts

router = APIRouter(prefix="/api/builds", tags=["builds"])
store = Orchestrator()
previews = PreviewService(store._build_repository)


def _preview_snapshot(build_id):
    try:
        build = store.get(build_id).model_copy(deep=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='Build not found') from exc
    artifacts = safe_artifacts(preview_artifacts(build))
    if not artifacts:
        raise HTTPException(status_code=404, detail='Generated source files are not available yet')
    return build, artifacts


@router.get('/{build_id}/preview', response_class=HTMLResponse)
async def open_preview(build_id: str):
    build, _ = _preview_snapshot(build_id)
    return HTMLResponse(preview_viewer(build), headers={'Content-Security-Policy': VIEWER_CSP,
                        'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})


@router.post('/{build_id}/preview/start', status_code=202)
async def start_preview(build_id: str, retry: bool = False):
    build, artifacts = _preview_snapshot(build_id)
    return await previews.start(build, artifacts, retry=retry)


@router.get('/{build_id}/preview/status')
async def preview_status(build_id: str):
    build, artifacts = _preview_snapshot(build_id)
    return await previews.status(build, artifacts)


@router.get('/{build_id}/preview/content', response_class=HTMLResponse)
async def preview_content(build_id: str):
    build, artifacts = _preview_snapshot(build_id)
    try:
        body = await previews.cached_html(build, artifacts)
    except PreviewError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return HTMLResponse(body, headers={'Content-Security-Policy': PREVIEW_CSP,
                        'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'no-store'})


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


@router.post("/{build_id}/retry-forge", status_code=202)
async def retry_forge(build_id: str):
    try:
        return await store.retry_forge(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{build_id}/retry-review", status_code=202)
async def retry_review(build_id: str):
    try:
        return await store.retry_review(build_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{build_id}/artifacts.zip")
async def download_artifacts(build_id: str):
    build, artifacts = _preview_snapshot(build_id)
    safe_title = re.sub(r"[^A-Za-z0-9_-]+", "-", build.title).strip("-")[:60] or "autoforge-project"
    return StreamingResponse(
        preview_zip(build, artifacts, previews),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}-{build.id}.zip"'},
    )


@router.post("/{build_id}/approve", status_code=202)
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


@router.post("/{build_id}/deployment-callback")
async def record_deployment_callback(
    build_id: str,
    payload: DeploymentCallback,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(default=None),
):
    expected = os.getenv("AUTOFORGE_DEPLOYMENT_CALLBACK_TOKEN", "")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid deployment callback credentials")
    if payload.status == "succeeded":
        parsed = urlparse(payload.url or "")
        if parsed.scheme != "https" or not parsed.netloc:
            raise HTTPException(status_code=422, detail="A valid HTTPS URL is required for successful deployment")
    try:
        build, queued = store.accept_deployment_callback(build_id, payload)
        if queued:
            from ..services.deployment_repair import repair_deployment
            background_tasks.add_task(repair_deployment, store, build_id, payload)
        return build
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Build not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
