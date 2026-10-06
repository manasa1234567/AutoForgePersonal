from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas.program import LearningProgramResponse, LearningProgramCreate
from ..core.auth import get_current_active_user, require_roles

router = APIRouter()

# Placeholder in-memory storage
fake_programs = [
    {"id": 1, "title": "Safety Training", "description": "Workplace safety basics.", "coordinator_id": 4, "start_date": "2024-01-01", "end_date": "2024-12-31", "active": True},
]

@router.get("/", response_model=List[LearningProgramResponse])
async def list_programs(current_user = Depends(get_current_active_user)):
    return fake_programs

@router.post("/", response_model=LearningProgramResponse)
async def create_program(program: LearningProgramCreate, current_user = Depends(require_roles(["coordinator", "admin"]))):
    new_id = len(fake_programs) + 1
    new_program = program.dict()
    new_program.update({"id": new_id, "start_date": None, "end_date": None, "active": True})
    fake_programs.append(new_program)
    # Would trigger workflows
    return new_program
