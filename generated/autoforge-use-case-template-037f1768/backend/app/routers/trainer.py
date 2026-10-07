from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas import TrainingProgramRead
from app.services.auth_service import require_role
from app.services.trainer_service import TrainerService

router = APIRouter()

@router.get("/participants", response_model=List[TrainingProgramRead])
async def get_participant_list(user=Depends(require_role(["Trainer"]))):
    service = TrainerService(user=user)
    participants = await service.get_participants()
    return participants

@router.post("/attendance")
async def record_attendance(session_id: int, participant_ids: List[int], user=Depends(require_role(["Trainer"]))):
    service = TrainerService(user=user)
    success = await service.record_attendance(session_id, participant_ids)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to record attendance.")
    return {"message": "Attendance recorded successfully."}
