from fastapi import APIRouter, HTTPException

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
