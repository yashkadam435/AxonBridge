import os
import uuid
import json
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from groq import AsyncGroq

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Persistence for encounters ──
DB_FILE = os.path.join(os.path.dirname(__file__), "encounters_db.json")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_db(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error saving DB: {e}")

encounters_db: Dict[str, dict] = load_db()

class EncounterCreate(BaseModel):
    patient_name: str
    patient_id: str = ""
    age: int = 0
    gender: str = "Unknown"
    encounter_type: str = "outpatient"
    department: str = "General"
    clinician: str = "Dr. Unknown"
    chief_complaint: str = ""
    symptoms: List[str] = Field(default_factory=list)
    history: str = ""
    vital_signs: Optional[Dict[str, Any]] = None
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)

class EncounterUpdate(BaseModel):
    patient_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    encounter_type: Optional[str] = None
    department: Optional[str] = None
    clinician: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[List[str]] = None
    history: Optional[str] = None
    vital_signs: Optional[Dict[str, Any]] = None
    current_medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

class SOAPRequest(BaseModel):
    encounter_id: str
    transcript: str = ""
    symptoms: List[str] = Field(default_factory=list)
    vital_signs: Optional[Dict[str, Any]] = None
    patient_context: Optional[Dict[str, Any]] = None

class SOAPUpdate(BaseModel):
    encounter_id: str
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""
    icd_codes: List[str] = Field(default_factory=list)

class PrescriptionRequest(BaseModel):
    encounter_id: str
    diagnosis: str
    patient_context: Dict[str, Any] = Field(default_factory=dict)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)

class ScribeParseRequest(BaseModel):
    transcript: str
    current_form_state: Dict[str, Any] = Field(default_factory=dict)

# ── Encounter CRUD ──

@router.post("/encounters")
async def create_encounter(data: EncounterCreate):
    enc_id = f"ENC-{str(uuid.uuid4())[:8].upper()}"
    patient_id = data.patient_id or f"PT-{str(uuid.uuid4())[:4].upper()}"
    encounter = {
        "id": enc_id,
        "patient_id": patient_id,
        "patient_name": data.patient_name,
        "age": data.age,
        "gender": data.gender,
        "encounter_type": data.encounter_type,
        "department": data.department,
        "clinician": data.clinician,
        "chief_complaint": data.chief_complaint,
        "symptoms": data.symptoms,
        "history": data.history,
        "vital_signs": data.vital_signs or {},
        "current_medications": data.current_medications,
        "allergies": data.allergies,
        "status": "active",
        "soap": None,
        "icd_codes": [],
        "prescriptions": [],
        "ai_confidence": 0.0,
        "soap_status": "pending"
    }
    encounters_db[enc_id] = encounter
    save_db(encounters_db)
    return encounter

@router.put("/encounters/{encounter_id}")
async def update_encounter(encounter_id: str, data: EncounterUpdate):
    enc = encounters_db.get(encounter_id)
    if not enc:
        return {"error": "Encounter not found"}
    
    update_data = data.dict(exclude_unset=True)
    for k, v in update_data.items():
        enc[k] = v
        
    encounters_db[encounter_id] = enc
    save_db(encounters_db)
    return enc

@router.get("/encounters")
async def list_encounters():
    # Return sorted by ID (newest first roughly)
    encs = list(encounters_db.values())
    encs.sort(key=lambda x: x["id"], reverse=True)
    return encs

@router.get("/encounters/{encounter_id}")
async def get_encounter(encounter_id: str):
    if encounter_id not in encounters_db:
        return {"error": "Encounter not found"}
    return encounters_db[encounter_id]

# ── Voice Scribe Parsing ──

@router.post("/scribe/parse")
async def parse_scribe_dictation(data: ScribeParseRequest):
    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    prompt = f"""You are AxonBridge Voice Scribe AI. Your job is to listen to clinical dictation and extract structured data.
You will be provided with the dictation transcript and the current state of the form.
Extract any new entities mentioned in the transcript and update the form state.

Current Form State: {json.dumps(data.current_form_state)}
New Transcript: "{data.transcript}"

Required Fields:
- patient_name (string)
- age (number)
- chief_complaint (string)

Rules:
1. Extract vitals into: vital_systolic, vital_diastolic, vital_hr, vital_spo2, vital_temp, vital_rr (only numbers).
2. Extract symptoms as a comma-separated string into 'symptoms'.
3. Extract history into 'history', current_medications into 'current_medications', allergies into 'allergies'.
4. If ANY of the Required Fields (patient_name, age, chief_complaint) are missing after parsing, generate a short, friendly spoken question in the 'tts_question' field to ask the user for the missing info (e.g. "I didn't catch the patient's age. What is it?").
5. If all required fields are present, set 'tts_question' to "Thank you, I have recorded the details. You can now generate the SOAP note or save the encounter."

Return ONLY valid JSON in this exact format:
{{
    "form_updates": {{
        "patient_name": "...",
        "age": 45,
        "chief_complaint": "...",
        ... other fields
    }},
    "tts_question": "Your spoken question here"
}}"""

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        parsed_data = json.loads(response.choices[0].message.content)
        return parsed_data
    except Exception as e:
        return {"error": str(e)}


# ── AI-powered SOAP Generation ──

@router.post("/soap/generate")
async def generate_soap(data: SOAPRequest):
    enc = encounters_db.get(data.encounter_id)
    if not enc:
        return {"error": "Encounter not found"}
    
    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    context_parts = []
    if enc.get("patient_name"):
        context_parts.append(f"Patient: {enc['patient_name']}, {enc.get('age', 'unknown')}yo {enc.get('gender', '')}")
    if enc.get("chief_complaint"):
        context_parts.append(f"Chief Complaint: {enc['chief_complaint']}")
    if enc.get("history"):
        context_parts.append(f"History: {enc['history']}")
    if data.symptoms or enc.get("symptoms"):
        symptoms = data.symptoms or enc.get("symptoms", [])
        context_parts.append(f"Symptoms: {', '.join(symptoms)}")
    if data.vital_signs or enc.get("vital_signs"):
        vitals = data.vital_signs or enc.get("vital_signs", {})
        context_parts.append(f"Vitals: {json.dumps(vitals)}")
    if enc.get("current_medications"):
        context_parts.append(f"Current Medications: {', '.join(enc['current_medications'])}")
    if enc.get("allergies"):
        context_parts.append(f"Allergies: {', '.join(enc['allergies'])}")
    if data.transcript:
        context_parts.append(f"Consultation Transcript: {data.transcript}")
    
    clinical_context = "\n".join(context_parts)
    
    prompt = f"""You are an expert clinical documentation AI for AxonBridge EHR. 
Generate a comprehensive SOAP note from the following clinical encounter.

{clinical_context}

Return ONLY valid JSON in this exact format:
{{
    "subjective": "Detailed subjective findings from patient history...",
    "objective": "Detailed objective findings from examination and vitals...",
    "assessment": "Clinical assessment with primary and differential diagnoses...",
    "plan": "Detailed treatment plan including medications, follow-up, referrals...",
    "icd_codes": ["CODE1", "CODE2"],
    "icd_descriptions": {{"CODE1": "Description 1", "CODE2": "Description 2"}},
    "confidence": 0.85,
    "severity": "moderate"
}}"""

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        soap_data = json.loads(response.choices[0].message.content)
        
        # Store in encounter
        enc["soap"] = soap_data
        enc["icd_codes"] = soap_data.get("icd_codes", [])
        enc["ai_confidence"] = soap_data.get("confidence", 0.0)
        enc["soap_status"] = "pending_review"
        save_db(encounters_db)
        
        return {"encounter_id": data.encounter_id, "soap": soap_data}
    except Exception as e:
        return {"error": str(e)}

# ── Save edited SOAP ──

@router.post("/soap/save")
async def save_soap(data: SOAPUpdate):
    enc = encounters_db.get(data.encounter_id)
    if not enc:
        return {"error": "Encounter not found"}
    
    enc["soap"] = {
        "subjective": data.subjective,
        "objective": data.objective,
        "assessment": data.assessment,
        "plan": data.plan,
    }
    enc["icd_codes"] = data.icd_codes
    enc["soap_status"] = "approved"
    save_db(encounters_db)
    
    return {"status": "saved", "encounter_id": data.encounter_id}

# ── AI Prescription Generator ──

@router.post("/prescriptions/generate")
async def generate_prescription(data: PrescriptionRequest):
    enc = encounters_db.get(data.encounter_id)
    if not enc:
        return {"error": "Encounter not found"}
    
    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    prompt = f"""You are a clinical pharmacology AI. Generate appropriate prescription recommendations.

Diagnosis: {data.diagnosis}
Patient: {json.dumps(data.patient_context)}
Allergies: {', '.join(data.allergies) if data.allergies else 'None reported'}
Current Medications: {', '.join(data.current_medications) if data.current_medications else 'None'}

Return ONLY valid JSON:
{{
    "prescriptions": [
        {{
            "medication": "Drug Name",
            "dosage": "Dosage",
            "route": "Oral/IV/etc",
            "frequency": "Frequency",
            "duration": "Duration",
            "notes": "Special instructions"
        }}
    ],
    "contraindications": ["Any warnings..."],
    "drug_interactions": ["Any interactions with current meds..."],
    "confidence": 0.85
}}"""
    
    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        rx_data = json.loads(response.choices[0].message.content)
        
        enc["prescriptions"] = rx_data.get("prescriptions", [])
        save_db(encounters_db)
        
        return {"encounter_id": data.encounter_id, "prescription_data": rx_data}
    except Exception as e:
        return {"error": str(e)}
