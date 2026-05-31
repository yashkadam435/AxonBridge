from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import BotRequest, BotResponse
from app.axonmd.bot_client import AxonMDBotClient
from app.axonmd.bot_definitions import BOT_DEFINITIONS

router = APIRouter()
bot_client = AxonMDBotClient()

@router.post("/invoke", response_model=BotResponse)
async def invoke_bot(request: BotRequest):
    context = {
        "symptoms": request.symptoms,
        "vitals": request.vital_signs,
        "history": request.patient_context,
        "diagnosis": request.current_diagnosis
    }
    return await bot_client.invoke_bot(request.specialty, context)

@router.post("/batch-invoke", response_model=List[BotResponse])
async def batch_invoke_bots(requests: List[BotRequest]):
    return await bot_client.batch_invoke(requests)

@router.get("/specialties")
async def list_specialties():
    return list(BOT_DEFINITIONS.keys())
