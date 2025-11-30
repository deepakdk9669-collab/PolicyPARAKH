from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..adk_agent.agents.auditor import AuditorAgent
from ..adk_agent.agents.critic import CriticAgent

router = APIRouter(
    prefix="/audit",
    tags=["audit"]
)

class AuditRequest(BaseModel):
    policy_text: str
    doc_type: str = "Insurance"

class AuditResponse(BaseModel):
    report: Dict[str, Any]
    critic_review: Optional[Dict[str, Any]] = None

@router.post("/", response_model=AuditResponse)
async def audit_policy(request: AuditRequest):
    try:
        auditor = AuditorAgent()
        report = auditor.audit_policy(request.policy_text, request.doc_type)
        
        # Optional: Run Critic
        critic = CriticAgent()
        review = critic.review_audit(request.policy_text, report)
        
        return AuditResponse(report=report, critic_review=review)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/full-report")
async def generate_full_report(request: AuditRequest):
    try:
        auditor = AuditorAgent()
        report_md = auditor.generate_full_report(request.policy_text)
        return {"report_markdown": report_md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
