from fastapi import APIRouter
from pydantic import BaseModel
from app.services.clinical_orchestrator import clinical_orchestrator, SOAPNoteData

router = APIRouter(prefix="/clinical", tags=["Clinical NLP"])

class AnalyzeTranscriptRequest(BaseModel):
    transcript: str

@router.post("/analyze", response_model=SOAPNoteData)
async def analyze_transcript(request: AnalyzeTranscriptRequest):
    """
    Takes a raw voice transcript, structures it into a SOAP note using the LLM,
    and extracts automation parameters.
    """
    return await clinical_orchestrator.process_transcript(request.transcript)
