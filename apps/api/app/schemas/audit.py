"""
AxonBridge — Audit Schemas
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    agent_session_id: UUID | None
    action: str
    action_category: str
    resource_type: str
    resource_id: str | None
    description: str | None
    details: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    severity: str
    integrity_hash: str
    timestamp: datetime
    screenshot_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogQuery(BaseModel):
    """Query parameters for audit log search."""
    user_id: UUID | None = None
    action: str | None = None
    action_category: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    severity: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class AuditIntegrityCheck(BaseModel):
    """Result of audit log integrity verification."""
    is_valid: bool
    total_entries_checked: int
    first_invalid_entry_id: UUID | None = None
    checked_at: datetime
