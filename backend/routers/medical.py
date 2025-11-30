from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..adk_agent.agents.medical_expert import MedicalExpertAgent

router = APIRouter(
    prefix="/medical",
    tags=["medical"]
)

class MedicalAnalysisRequest(BaseModel):
    query: str
    policy_context: str = ""

@router.post("/analyze")
async def analyze_report(request: MedicalAnalysisRequest):
    try:
        expert = MedicalExpertAgent()
        analysis = expert.analyze_medical_report(request.query, request.policy_context)
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explain/{term}")
async def explain_term(term: str):
    try:
        expert = MedicalExpertAgent()
        explanation = expert.explain_term(term)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
