from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.core.llm_client import llm_client

class SOAPNoteData(BaseModel):
    subjective: str = Field(description="Patient's subjective complaints and history")
    objective: str = Field(description="Objective clinical findings, vitals, physical exam")
    assessment: str = Field(description="Clinical assessment and diagnosis")
    plan: str = Field(description="Treatment plan, medications, follow-up")
    extracted_parameters: Dict[str, Any] = Field(description="Key-value pairs of strictly extracted parameters like MRN, Patient Name, Medication, Dosage")

class ClinicalOrchestrator:
    """Orchestrates the conversion of Voice Transcripts into Structured Clinical Actions"""
    
    async def process_transcript(self, raw_transcript: str) -> SOAPNoteData:
        """
        Takes raw voice text and uses the LLM to structure it into a SOAP note 
        and extract portal automation parameters.
        """
        system_prompt = (
            "You are an expert clinical AI physician. Your job is to take raw, messy Voice-to-Text "
            "transcripts (which could be in any language) and structure them into a formal SOAP note in English. "
            "CRITICAL: You must actively formulate an Assessment (likely diagnosis) and a comprehensive Plan. "
            "The Plan MUST include specific recommended medications, prescriptions, dosages, and follow-up advice based on standard medical guidelines. "
            "Additionally, extract exact parameters (Patient Name, Age, Symptoms, Diagnoses, Prescribed Medications) into a JSON dictionary "
            "for RPA automation."
        )
        
        prompt = f"Transcript:\n{raw_transcript}"
        
        # Call the LLM (which automatically enforces the SOAPNoteData JSON schema)
        result = await llm_client.generate_structured(
            prompt=prompt,
            schema=SOAPNoteData,
            system_prompt=system_prompt
        )
        
        # If running locally without an API key, provide mock data for the demo
        if not result.subjective:
            return SOAPNoteData(
                subjective="Patient complains of chest pain (MOCK DATA - Missing API Key)",
                objective="BP 140/90, HR 88",
                assessment="Possible angina",
                plan="ECG, Nitroglycerin",
                extracted_parameters={"Patient Name": "John Doe", "Medication": "Nitroglycerin"}
            )
            
        return result

clinical_orchestrator = ClinicalOrchestrator()
