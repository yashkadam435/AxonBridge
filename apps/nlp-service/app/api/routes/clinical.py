from fastapi import APIRouter
from pydantic import BaseModel
from app.clinical_nlp.soap_structurer import SOAPStructurer

router = APIRouter()
soap_structurer = SOAPStructurer()

class TranscriptRequest(BaseModel):
    transcript: str
    language: str = "en"

@router.post("/structure-soap")
async def structure_soap(request: TranscriptRequest):
    return await soap_structurer.structure(request.transcript, request.language)
