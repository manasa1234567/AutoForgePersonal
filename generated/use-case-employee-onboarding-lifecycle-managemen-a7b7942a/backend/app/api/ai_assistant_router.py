from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.api.auth_router import get_current_user, User
from app.services.ai_assistant_service import AIAssistantService

router = APIRouter()

class AIQueryRequest(BaseModel):
    query: str

class AIResponse(BaseModel):
    response: str

@router.post("/query", response_model=AIResponse)
async def query_ai_assistant(request: AIQueryRequest, current_user: User = Depends(get_current_user)):
    # Permissions can be refined
    answer = await AIAssistantService.process_query(request.query, current_user)
    if answer is None:
        raise HTTPException(status_code=400, detail="Cannot process the query.")
    return AIResponse(response=answer)
