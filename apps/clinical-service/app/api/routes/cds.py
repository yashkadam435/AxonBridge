import os
import uuid
from fastapi import APIRouter
from app.models.schemas import BotRequest, CDSOverlay
from app.cds.cds_engine import CDSEngine

router = APIRouter()

def get_db_url():
    url = os.getenv("POSTGRES_URL", "postgresql+asyncpg://axonbridge:changeme_secure_password_here@axonbridge-postgres:5432/axonbridge")
    return url.replace("postgresql+asyncpg://", "postgresql://")

@router.post("/evaluate", response_model=CDSOverlay)
async def evaluate_context(request: BotRequest):
    engine = CDSEngine(get_db_url())
    session_id = str(uuid.uuid4())
    return await engine.evaluate(request, session_id)
