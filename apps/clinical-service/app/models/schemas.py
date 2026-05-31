from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class BotRequest(BaseModel):
    specialty: str
    patient_context: Dict[str, Any] = Field(default_factory=dict)
    symptoms: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    vital_signs: Optional[Dict[str, Any]] = None
    lab_results: Optional[List[Dict[str, Any]]] = None
    current_diagnosis: Optional[str] = None
    department: Optional[str] = None
    urgency: str = "routine"  # routine, urgent, emergency

class BotResponse(BaseModel):
    specialty: str
    bot_version: str
    response_type: str  # differential, investigation, treatment, alert
    content: Dict[str, Any]
    confidence: float
    citations: List[str] = Field(default_factory=list)
    requires_immediate_attention: bool = False
    processing_time_ms: int = 0
    cached: bool = False

class CDSAction(BaseModel):
    label: str
    action_type: str  # order, review, warn, info
    target_his_element: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    auto_executable: bool = False

class CDSAlert(BaseModel):
    id: str
    priority: str  # emergency, high, medium, low, informational
    category: str  # differential, investigation, treatment, drug_safety, preventive
    title: str
    description: str
    evidence_level: str  # A, B, C, consensus, expert_opinion
    source: str
    confidence: float
    actions: List[CDSAction] = Field(default_factory=list)
    override_allowed: bool = True
    requires_acknowledgment: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CDSOverlay(BaseModel):
    session_id: str
    alerts: List[CDSAlert]
    summary: str
    total_alerts: int
    emergency_count: int
    requires_acknowledgment: bool
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    validity_seconds: int = 300

class AnomalyAlert(BaseModel):
    id: str
    type: str
    field: str
    value: Any
    expected_range: str
    severity: str  # critical, warning
    message: str
    suggested_action: str

class ConfidenceScore(BaseModel):
    action_id: str
    action_type: str
    overall_score: float
    factor_scores: Dict[str, float]
    threshold: float
    escalated: bool
    escalation_reason: Optional[str] = None
    recommended_action: str
    historical_comparison: Optional[Dict[str, Any]] = None

class EncounterConfidence(BaseModel):
    encounter_id: str
    overall_score: float
    action_scores: List[ConfidenceScore]
    items_requiring_review: List[str]
    items_approved: List[str]
    estimated_review_time_seconds: int
    risk_level: str
