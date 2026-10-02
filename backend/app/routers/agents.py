from fastapi import APIRouter

from ..models.schemas import SpecAgentRequest
from ..services.agent_service import AgentService

router = APIRouter(prefix="/api/agents", tags=["agents"])

service = AgentService()


@router.post("/spec/analyze")
async def analyze_spec(payload: SpecAgentRequest):
    result = await service.run_spec_agent(
        title=payload.title,
        source_type=payload.source_type,
        source_text=payload.source_text,
    )

    return {
        "agent": "Spec Agent",
        "status": "completed",
        "summary": result.summary,
        "requirements": result.requirements,
        "acceptanceCriteria": result.acceptance_criteria,
        "dependencies": result.dependencies,
        "constraints": result.constraints,
        "ambiguities": result.ambiguities,
        "assumptions": result.assumptions,
        "risks": result.risks,
        "securityConsiderations": result.security_considerations,
        "clarificationQuestions": result.clarification_questions,
        "confidence": result.confidence,
        "readiness": result.readiness,
        "tokens": result.tokens,
        "mode": result.mode,
    }