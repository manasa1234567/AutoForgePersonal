from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import TrainingProgramCreate, TrainingProgramRead
from app.services.auth_service import require_role
from app.services.coordinator_service import CoordinatorService

router = APIRouter()

@router.post("/programs", response_model=TrainingProgramRead, status_code=status.HTTP_201_CREATED)
async def create_training_program(
    program_create: TrainingProgramCreate,
    user=Depends(require_role(["Coordinator"]))
):
    service = CoordinatorService(user=user)
    program = await service.create_program(program_create)
    return program

@router.get("/programs", response_model=List[TrainingProgramRead])
async def list_programs(user=Depends(require_role(["Coordinator"]))):
    service = CoordinatorService(user=user)
    programs = await service.list_programs()
    return programs
