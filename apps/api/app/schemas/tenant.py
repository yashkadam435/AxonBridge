"""
AxonBridge — Tenant Schemas
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    """Create a new tenant (healthcare organization)."""
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    admin_email: str | None = None
    admin_phone: str | None = None
    subscription_tier: str = "standard"
    compliance_region: str = Field(default="us", pattern="^(us|eu|in|ae|uk|sg)$")
    config: dict[str, Any] = Field(default_factory=dict)


class TenantUpdate(BaseModel):
    """Update an existing tenant."""
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    admin_email: str | None = None
    admin_phone: str | None = None
    subscription_tier: str | None = None
    compliance_region: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None


class TenantResponse(BaseModel):
    """Tenant response."""
    id: UUID
    name: str
    slug: str
    description: str | None
    is_active: bool
    subscription_tier: str
    compliance_region: str
    config: dict[str, Any]
    admin_email: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TenantSummary(BaseModel):
    """Minimal tenant info for lists."""
    id: UUID
    name: str
    slug: str
    is_active: bool
    subscription_tier: str

    model_config = {"from_attributes": True}
