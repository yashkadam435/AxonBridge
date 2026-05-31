import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import AsyncGroq

router = APIRouter()

class AnalyzeTranscriptRequest(BaseModel):
    transcript: str

@router.post("/analyze")
async def analyze_transcript(request: AnalyzeTranscriptRequest):
    api_key = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    if api_key == "your_groq_api_key_here":
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on server.")
        
    groq_client = AsyncGroq(api_key=api_key)
    
    system_prompt = (
        "You are an expert clinical AI physician. Your job is to take raw, messy Voice-to-Text "
        "transcripts and structure them into a formal SOAP note in English. "
        "CRITICAL: You must actively formulate an Assessment (likely diagnosis) and a comprehensive Plan. "
        "The Plan MUST include specific recommended medications, prescriptions, dosages, and follow-up advice based on standard medical guidelines. "
        "Additionally, extract exact parameters (Patient Name, Age, Symptoms, Diagnoses, Prescribed Medications) into a JSON dictionary "
        "for RPA automation. "
        "Respond STRICTLY in JSON with the following exact keys: subjective, objective, assessment, plan, extracted_parameters. "
        "extracted_parameters should be a dictionary of strings."
    )
    
    prompt = f"Transcript:\n{request.transcript}"
    
    try:
        response = await groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = json.loads(response.choices[0].message.content)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
