"""
AxonBridge — Workflow Schemas
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    category: str = "general"
    his_target_id: UUID | None = None
    mode: str = Field(default="assisted", pattern="^(assisted|automated)$")
    risk_level: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    steps_config: list[dict[str, Any]] = Field(default_factory=list)
    trigger_config: dict[str, Any] | None = None
    retry_config: dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff_seconds": 5})


class WorkflowTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    mode: str | None = None
    risk_level: str | None = None
    steps_config: list[dict[str, Any]] | None = None
    trigger_config: dict[str, Any] | None = None
    is_active: bool | None = None


class WorkflowTemplateResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    category: str
    his_target_id: UUID | None
    mode: str
    risk_level: str
    is_active: bool
    version: int
    steps_config: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowExecutionResponse(BaseModel):
    id: UUID
    template_id: UUID | None
    initiated_by: UUID | None
    status: str
    current_step: int
    total_steps: int
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None
    error_log: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
