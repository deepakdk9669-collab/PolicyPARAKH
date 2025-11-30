from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..adk_agent.utils.ai_engine import AIEngine

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class ChatRequest(BaseModel):
    message: str
    context: str = ""

@router.post("/")
async def chat(request: ChatRequest):
    try:
        engine = AIEngine()
        response = engine.run_genesis_agent(request.message, request.context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
