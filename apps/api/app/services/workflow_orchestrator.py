from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.core.llm_client import llm_client

# 1. Patient Registration Schema
class PatientRegistrationSchema(BaseModel):
    patient_name: str = Field(description="Full name of the patient")
    dob: str = Field(description="Date of birth")
    gender: str = Field(description="Gender of the patient")
    contact_number: str = Field(description="Phone or contact number")
    address: str = Field(description="Full address of the patient")
    insurance_provider: str = Field(description="Name of the insurance provider")
    policy_number: str = Field(description="Insurance policy number")
    emergency_contact: str = Field(description="Emergency contact name and number")

# 2. Billing Code Entry Schema
class BillingCodeSchema(BaseModel):
    icd_10_codes: List[str] = Field(description="List of extracted ICD-10 diagnostic codes")
    cpt_codes: List[str] = Field(description="List of extracted CPT procedure codes")
    primary_diagnosis: str = Field(description="The primary diagnosis text")
    justification: str = Field(description="Brief justification for the selected codes based on the clinical text")

# 3. Lab Result Extraction Schema
class LabResultItem(BaseModel):
    test_name: str = Field(description="Name of the laboratory test")
    value: str = Field(description="The measured value")
    unit: str = Field(description="Unit of measurement")
    reference_range: str = Field(description="Normal reference range for the test")
    flag: str = Field(description="Flag indicating if it's High, Low, or Normal")

class LabResultSchema(BaseModel):
    patient_name: str = Field(description="Patient Name")
    collection_date: str = Field(description="Date the sample was collected")
    results: List[LabResultItem] = Field(description="List of extracted lab results")
    abnormal_findings: List[str] = Field(description="List of any critically abnormal findings")

# 4. Discharge Summary Schema
class DischargeSummarySchema(BaseModel):
    patient_name: str = Field(description="Name of the patient")
    admission_date: str = Field(description="Date of admission")
    discharge_date: str = Field(description="Date of discharge")
    chief_complaint: str = Field(description="Primary reason for admission")
    hospital_course: str = Field(description="Brief summary of the hospital course and treatments")
    discharge_diagnoses: List[str] = Field(description="List of final diagnoses at discharge")
    discharge_medications: List[str] = Field(description="List of medications prescribed at discharge")
    follow_up_instructions: str = Field(description="Instructions for follow-up care")

# 5. Appointment Scheduling Schema
class AppointmentSchedulingSchema(BaseModel):
    patient_name: str = Field(description="Name of the patient")
    requested_doctor: str = Field(description="Name or specialty of the requested provider")
    requested_date: str = Field(description="Requested date for the appointment")
    requested_time: str = Field(description="Requested time preference (e.g., Morning, 2:00 PM)")
    reason_for_visit: str = Field(description="Primary reason for the appointment")
    urgency: str = Field(description="Urgency level: Routine, Urgent, Emergency")

class WorkflowOrchestrator:
    """Orchestrates dynamic AI workflow executions based on type."""
    
    async def process_workflow(self, workflow_type: str, raw_text: str) -> Dict[str, Any]:
        """Routes the text to the correct LLM prompt and schema based on the workflow ID."""
        
        prompt = f"Extract and structure the following data based on the provided text:\n\n{raw_text}"
        
        if workflow_type == "registration":
            system_prompt = "You are an expert medical administrative assistant. Your task is to extract patient demographic and insurance details from raw text and perfectly map them to the JSON schema. Leave fields blank if the information is completely missing."
            result = await llm_client.generate_structured(prompt, PatientRegistrationSchema, system_prompt)
            return result.model_dump()
            
        elif workflow_type == "billing":
            system_prompt = "You are an expert medical coder. Your task is to extract clinical diagnoses and procedures from the clinical text and map them accurately to ICD-10 and CPT codes. Return a structured JSON."
            result = await llm_client.generate_structured(prompt, BillingCodeSchema, system_prompt)
            return result.model_dump()
            
        elif workflow_type == "lab-results":
            system_prompt = "You are a clinical data extraction engine. Parse the unstructured laboratory report text into structured key-value pairs. Identify abnormal flags."
            result = await llm_client.generate_structured(prompt, LabResultSchema, system_prompt)
            return result.model_dump()
            
        elif workflow_type == "discharge":
            system_prompt = "You are a physician assistant AI. Your job is to take rough unstructured physician notes and synthesize a formal structured Discharge Summary."
            result = await llm_client.generate_structured(prompt, DischargeSummarySchema, system_prompt)
            return result.model_dump()
            
        elif workflow_type == "scheduling":
            system_prompt = "You are a medical scheduling assistant. Extract appointment request details from the raw message, including patient name, doctor, timing, and urgency."
            result = await llm_client.generate_structured(prompt, AppointmentSchedulingSchema, system_prompt)
            return result.model_dump()
            
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

workflow_orchestrator = WorkflowOrchestrator()
