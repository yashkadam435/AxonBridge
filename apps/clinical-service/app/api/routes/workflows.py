import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import AsyncGroq

router = APIRouter()

class WorkflowAnalyzeRequest(BaseModel):
    workflow_type: str
    text: str

@router.post("/analyze")
async def analyze_workflow(request: WorkflowAnalyzeRequest):
    api_key = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    if api_key == "your_groq_api_key_here":
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on server.")
        
    groq_client = AsyncGroq(api_key=api_key)
    
    schemas = {
        "registration": "Keys: patient_name, dob, gender, contact_number, address, insurance_provider, policy_number, emergency_contact",
        "billing": "Keys: icd_10_codes (list), cpt_codes (list), primary_diagnosis, justification",
        "lab-results": "Keys: patient_name, collection_date, results (list of objects with test_name, value, unit, reference_range, flag), abnormal_findings (list)",
        "discharge": "Keys: patient_name, admission_date, discharge_date, chief_complaint, hospital_course, discharge_diagnoses (list), discharge_medications (list), follow_up_instructions",
        "scheduling": "Keys: patient_name, requested_doctor, requested_date, requested_time, reason_for_visit, urgency"
    }

    if request.workflow_type not in schemas:
        raise HTTPException(status_code=400, detail=f"Unknown workflow type: {request.workflow_type}")
        
    system_prompt = (
        f"You are an expert medical AI assistant. Your task is to extract clinical data from the following unstructured text "
        f"and return it STRICTLY as a JSON object matching this structure for the '{request.workflow_type}' workflow:\n"
        f"{schemas[request.workflow_type]}\n"
        f"Return ONLY valid JSON."
    )
    
    prompt = f"Text:\n{request.text}"
    
    try:
        response = await groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        content = json.loads(response.choices[0].message.content)
        return {"status": "success", "data": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
