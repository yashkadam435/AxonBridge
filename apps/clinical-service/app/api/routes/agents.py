import os
import uuid
import json
import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from groq import AsyncGroq

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

DB_FILE = os.path.join(os.path.dirname(__file__), "agents_db.json")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"agents": {}, "pending_actions": []}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load_db()

class NewAgentRequest(BaseModel):
    his: str = "eHospital"
    workflow: str = "Patient Registration"
    mode: str = "assisted"

@router.get("")
async def list_agents():
    # Return active agents with newest first
    agents_list = list(db["agents"].values())
    agents_list.sort(key=lambda x: x.get("start_time", 0), reverse=True)
    return {
        "agents": agents_list,
        "pending_actions": db["pending_actions"]
    }

@router.post("/new")
async def create_agent(req: NewAgentRequest):
    agent_id = f"Agent-{random.randint(100, 999)}"
    agent = {
        "id": agent_id,
        "name": agent_id,
        "status": "active",
        "his": req.his,
        "workflow": req.workflow,
        "progress": 0,
        "actions": 0,
        "confidence": 0.95,
        "mode": req.mode,
        "uptime": "0h 0m",
        "start_time": datetime.now().timestamp(),
        "history": []
    }
    db["agents"][agent_id] = agent
    save_db(db)
    return agent

@router.post("/{agent_id}/simulate")
async def simulate_agent_step(agent_id: str):
    agent = db["agents"].get(agent_id)
    if not agent or agent["status"] != "active":
        return {"status": "ignored"}
        
    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    prompt = f"""You are simulating an RPA agent executing the workflow: {agent['workflow']} on the system: {agent['his']}.
Current progress: {agent['progress']}%
Actions completed: {agent['actions']}
Recent history: {agent.get('history', [])[-3:]}

Based on the progress, what is the next logical action?
Is this action critical enough to require Human-in-the-Loop (HITL) approval? (e.g. submitting data, saving a record, processing a bill, finalizing).

Return ONLY valid JSON:
{{
    "progress_increment": (integer between 15 and 30),
    "action_description": "short description of the action to take (e.g. 'Read lab results from panel', 'Submit ICD-10 code')",
    "requires_hitl": (boolean - true if it modifies system data or finalizes, false if it just navigates or reads),
    "confidence": (float 0.70 to 0.99)
}}"""

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        sim = json.loads(response.choices[0].message.content)
        
        agent["progress"] = min(100, agent["progress"] + sim.get("progress_increment", 20))
        agent["actions"] += 1
        agent["confidence"] = sim.get("confidence", 0.95)
        
        # update uptime string
        uptime_mins = int((datetime.now().timestamp() - agent["start_time"]) / 60)
        agent["uptime"] = f"0h {uptime_mins}m"
        
        if agent["progress"] >= 100:
            agent["status"] = "completed"
        elif sim.get("requires_hitl", False) and agent["mode"] == "assisted":
            agent["status"] = "waiting_confirmation"
            pa_id = f"pa-{uuid.uuid4().hex[:6]}"
            db["pending_actions"].append({
                "id": pa_id,
                "agent": agent_id,
                "action": sim.get("action_description", "Critical System Action"),
                "confidence": agent["confidence"],
                "screenshot": True,
                "timestamp": "Just now"
            })
            
        if "history" not in agent:
            agent["history"] = []
        agent["history"].append(sim.get("action_description", ""))
        save_db(db)
        return {"status": "success", "agent": agent}
    except Exception as e:
        print(f"Error simulating: {e}")
        return {"status": "error"}

@router.post("/actions/{action_id}/approve")
async def approve_action(action_id: str):
    pa = next((x for x in db["pending_actions"] if x["id"] == action_id), None)
    if pa:
        db["pending_actions"].remove(pa)
        agent = db["agents"].get(pa["agent"])
        if agent:
            agent["status"] = "active"
            if agent["progress"] >= 100:
                agent["status"] = "completed"
        save_db(db)
    return {"status": "approved"}

@router.post("/actions/{action_id}/reject")
async def reject_action(action_id: str):
    pa = next((x for x in db["pending_actions"] if x["id"] == action_id), None)
    if pa:
        db["pending_actions"].remove(pa)
        agent = db["agents"].get(pa["agent"])
        if agent:
            agent["status"] = "error" # Rejected actions cause agent to error out
        save_db(db)
    return {"status": "rejected"}
    
@router.post("/abort_all")
async def abort_all():
    for agent in db["agents"].values():
        if agent["status"] in ["active", "waiting_confirmation", "initializing"]:
            agent["status"] = "paused"
    db["pending_actions"] = []
    save_db(db)
    return {"status": "aborted"}
