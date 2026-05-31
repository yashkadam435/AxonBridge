"""
AxonBridge — Agent Schemas
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentSessionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    workflow_execution_id: UUID | None
    his_target_id: UUID | None
    status: str
    mode: str
    started_at: datetime | None
    ended_at: datetime | None
    total_actions: int
    successful_actions: int
    failed_actions: int
    human_interventions: int
    last_error: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentActionResponse(BaseModel):
    id: UUID
    session_id: UUID
    action_type: str
    action_description: str | None
    target_element: str | None
    result_status: str
    confidence_score: float | None
    requires_human_approval: bool
    human_decision: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    error_message: str | None

    model_config = {"from_attributes": True}


class HITLDecisionRequest(BaseModel):
    """Human-in-the-loop decision on an agent action."""
    decision: str = Field(pattern="^(approved|modified|rejected)$")
    modification: dict[str, Any] | None = None
    reason: str | None = None
