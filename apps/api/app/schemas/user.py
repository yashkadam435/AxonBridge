"""
AxonBridge — User Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Create a new user."""
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=12)
    title: str | None = None
    department: str | None = None
    language_preference: str = "en"
    role_ids: list[UUID] = Field(default_factory=list, description="Role IDs to assign")


class UserUpdate(BaseModel):
    """Update user profile."""
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    title: str | None = None
    department: str | None = None
    language_preference: str | None = None
    theme_preference: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """User profile response (excludes sensitive fields)."""
    id: UUID
    tenant_id: UUID
    email: str
    full_name: str
    title: str | None
    department: str | None
    is_active: bool
    mfa_enabled: bool
    last_login: datetime | None
    language_preference: str
    theme_preference: str
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime
    roles: list["RoleSummary"] = []

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Minimal user info for lists."""
    id: UUID
    email: str
    full_name: str
    is_active: bool
    title: str | None = None

    model_config = {"from_attributes": True}


class UserProfile(BaseModel):
    """Extended user profile with roles and permissions."""
    id: UUID
    tenant_id: UUID
    email: str
    full_name: str
    title: str | None
    department: str | None
    is_active: bool
    mfa_enabled: bool
    language_preference: str
    theme_preference: str
    avatar_url: str | None
    roles: list["RoleSummary"] = []
    permissions: list[str] = Field(
        default_factory=list,
        description="Flat list of permissions: 'resource:action'"
    )

    model_config = {"from_attributes": True}


class RoleSummary(BaseModel):
    """Minimal role info for embedding in user responses."""
    id: UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


# Fix forward references
UserResponse.model_rebuild()
UserProfile.model_rebuild()
