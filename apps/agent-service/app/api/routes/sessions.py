"""
Sessions API Route
"""
import uuid
from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("")
async def create_session():
    session_id = str(uuid.uuid4())
    return {"id": session_id, "status": "initializing"}

@router.get("")
async def list_sessions():
    return {"items": []}
