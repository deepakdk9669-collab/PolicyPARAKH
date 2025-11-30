from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..adk_agent.agents.lawyer import CourtroomAgent

router = APIRouter(
    prefix="/courtroom",
    tags=["courtroom"]
)

class SimulationRequest(BaseModel):
    history: List[Dict[str, Any]]
    context: str

@router.post("/simulate-turn")
async def simulate_turn(request: SimulationRequest):
    try:
        court = CourtroomAgent()
        turn = court.simulate_turn(request.history, request.context)
        return turn
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
