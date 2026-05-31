"""
AxonBridge — Clinical Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EncounterCreate(BaseModel):
    encounter_id: str = Field(description="External encounter ID (will be encrypted)")
    patient_id: str = Field(description="External patient ID (will be encrypted)")
    patient_name: str | None = None
    encounter_type: str = "outpatient"
    encounter_date: datetime
    department: str | None = None
    his_source: str | None = None


class EncounterResponse(BaseModel):
    id: UUID
    encounter_type: str
    encounter_date: datetime
    department: str | None
    status: str
    his_source: str | None
    clinician_id: UUID | None
    created_at: datetime
    # Note: encrypted fields are NOT exposed

    model_config = {"from_attributes": True}


class SOAPNoteResponse(BaseModel):
    id: UUID
    encounter_id: UUID
    icd_codes: list | None
    snomed_codes: list | None
    loinc_codes: list | None
    generated_by: str
    confidence_score: float | None
    is_approved: bool
    approved_by: UUID | None
    approved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
