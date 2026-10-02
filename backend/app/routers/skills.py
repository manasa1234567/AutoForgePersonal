from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from ..models.schemas import SkillApprovalRequest, SkillRecipe, SkillStatus
from ..services.skill_registry import skill_registry

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=list[SkillRecipe])
async def list_skills(
    status: SkillStatus | None = None,
    agent: str | None = None,
    q: Annotated[str, Query(max_length=200)] = "",
) -> list[SkillRecipe]:
    return skill_registry.list(status=status, agent=agent, query=q)


@router.get("/{recipe_id}", response_model=SkillRecipe)
async def get_skill(recipe_id: str) -> SkillRecipe:
    try:
        return skill_registry.get(recipe_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{recipe_id}/decision", response_model=SkillRecipe)
async def decide_skill(recipe_id: str, request: SkillApprovalRequest) -> SkillRecipe:
    try:
        return skill_registry.decide(recipe_id, decision=request.decision, reason=request.reason)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
