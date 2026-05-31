"""
AxonBridge — Schemas Package

Pydantic request/response schemas for API validation.
"""

from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
    HealthCheck,
    IDResponse,
    DeleteResponse,
)
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, PermissionResponse
from app.schemas.audit import AuditLogResponse, AuditLogQuery
from app.schemas.workflow import WorkflowTemplateCreate, WorkflowTemplateResponse
from app.schemas.clinical import EncounterCreate, EncounterResponse
from app.schemas.agent import AgentSessionResponse, AgentActionResponse, HITLDecisionRequest

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "HealthCheck",
    "IDResponse",
    "DeleteResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "PermissionResponse",
    "AuditLogResponse",
    "AuditLogQuery",
    "WorkflowTemplateCreate",
    "WorkflowTemplateResponse",
    "EncounterCreate",
    "EncounterResponse",
    "AgentSessionResponse",
    "AgentActionResponse",
    "HITLDecisionRequest",
]
