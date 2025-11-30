from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

DATA_DIR = "data"
INTEL_FILE = os.path.join(DATA_DIR, "market_intel.json")
REQUESTS_FILE = os.path.join(DATA_DIR, "admin_requests.json")

class AdminRequest(BaseModel):
    id: Optional[str] = None
    tool: str
    message: str
    status: str = "PENDING"
    timestamp: str

class UpdateStatusRequest(BaseModel):
    status: str

@router.get("/dashboard-stats")
async def get_dashboard_stats():
    try:
        if os.path.exists(INTEL_FILE):
            with open(INTEL_FILE, "r") as f:
                data = json.load(f)
            return data
        return {"error": "Market Intel not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests")
async def get_requests():
    try:
        if os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/requests/{index}/status")
async def update_request_status(index: int, update: UpdateStatusRequest):
    try:
        if os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "r") as f:
                data = json.load(f)
            
            # Sort to match frontend display if needed, but index reliance is risky.
            # Ideally we use IDs. For now, assuming consistent order or simple list.
            # To be safe, let's just update by index if valid.
            if 0 <= index < len(data):
                data[index]["status"] = update.status
                with open(REQUESTS_FILE, "w") as f:
                    json.dump(data, f, indent=2)
                return {"message": "Status updated"}
            else:
                raise HTTPException(status_code=404, detail="Request not found")
        return {"error": "No requests file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-agent")
async def trigger_agent(agent_name: str = Body(...), payload: Dict[str, Any] = Body(...)):
    """
    God Mode: Manually trigger any agent with custom payload.
    """
    try:
        # Dynamic import to avoid circular deps if possible, or just standard import
        from ..adk_agent.utils.ai_engine import AIEngine
        engine = AIEngine()
        
        # This is a simplified "God Mode" trigger. 
        # In a real app, we'd map agent_name to specific classes.
        # For now, we'll just use the engine's router or specific methods.
        
        return {"status": "Triggered", "agent": agent_name, "result": "Simulation started (Mock)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
