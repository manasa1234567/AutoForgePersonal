from io import BytesIO
from html import escape, unescape
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
    body = re.search(r"<body\b[^>]*>(.*?)</body\s*>", preview or "", flags=re.IGNORECASE | re.DOTALL)
    visible = re.sub(r"<(script|style|template)\b[^>]*>.*?</\1\s*>", " ", body.group(1) if body else "", flags=re.IGNORECASE | re.DOTALL)
    visible = re.sub(r"<[^>]+>", " ", visible)
    if not unescape(visible).strip():
        requirement_items = "".join(
            f"<li>{escape(item.text)}</li>" for item in build.requirements[:8]
        ) or "<li>Review the approved application workflow.</li>"
        preview = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(build.title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f6fb;color:#20283a;font:16px/1.5 system-ui,sans-serif}}header{{padding:28px 7%;background:#172b4d;color:white}}main{{max-width:960px;margin:32px auto;padding:0 20px}}.label{{color:#6751c8;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}}section{{padding:24px;border:1px solid #e0e5ef;border-radius:14px;background:white}}li{{margin:12px 0}}
</style></head><body><header><span>Application preview</span><h1>{escape(build.title)}</h1><p>Visual concept from the approved use case</p></header><main><section><strong class="label">Planned capabilities</strong><ul>{requirement_items}</ul></section></main></body></html>'''
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
