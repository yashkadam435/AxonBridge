"""
AxonBridge — Role & Permission Schemas
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionCreate(BaseModel):
    """Create a new permission."""
    resource: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=50)
    description: str | None = None
    conditions: dict[str, Any] | None = None


class PermissionResponse(BaseModel):
    """Permission response."""
    id: UUID
    resource: str
    action: str
    description: str | None
    conditions: dict[str, Any] | None

    model_config = {"from_attributes": True}

    @property
    def key(self) -> str:
        return f"{self.resource}:{self.action}"


class RoleCreate(BaseModel):
    """Create a new role."""
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    priority: int = 0
    permission_ids: list[UUID] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Update a role."""
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    priority: int | None = None
    permission_ids: list[UUID] | None = None


class RoleResponse(BaseModel):
    """Role response with permissions."""
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    is_system_role: bool
    priority: int
    permissions: list[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleAssignment(BaseModel):
    """Assign or unassign a role."""
    user_id: UUID
    role_id: UUID


class RoleSummary(BaseModel):
    """Minimal role info."""
    id: UUID
    name: str
    is_system_role: bool

    model_config = {"from_attributes": True}
