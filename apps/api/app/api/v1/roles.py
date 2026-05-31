"""
AxonBridge — Role & Permission Routes
"""

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import (
    get_current_tenant_id,
    get_rbac_service,
    require_permission,
)
from app.models.user import User
from app.schemas.common import SuccessResponse, IDResponse, DeleteResponse
from app.schemas.role import (
    PermissionResponse,
    RoleAssignment,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.services.rbac_service import RBACService

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@router.post("", response_model=IDResponse, status_code=201)
async def create_role(
    data: RoleCreate,
    _: User = Depends(require_permission("roles", "create")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    service: RBACService = Depends(get_rbac_service),
):
    """Create a custom role."""
    role = await service.create_role(tenant_id, data)
    return IDResponse(id=role.id, message="Role created successfully")


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    _: User = Depends(require_permission("roles", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    service: RBACService = Depends(get_rbac_service),
):
    """List all roles for the current tenant."""
    roles = await service.list_roles(tenant_id)
    return [RoleResponse.model_validate(r) for r in roles]


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    _: User = Depends(require_permission("roles", "read")),
    service: RBACService = Depends(get_rbac_service),
):
    """List all available permissions."""
    perms = await service.list_permissions()
    return [PermissionResponse.model_validate(p) for p in perms]


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: uuid.UUID,
    _: User = Depends(require_permission("roles", "read")),
    service: RBACService = Depends(get_rbac_service),
):
    """Get a specific role."""
    role = await service.get_role(role_id)
    return RoleResponse.model_validate(role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    data: RoleUpdate,
    _: User = Depends(require_permission("roles", "update")),
    service: RBACService = Depends(get_rbac_service),
):
    """Update a role."""
    role = await service.update_role(role_id, data)
    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", response_model=DeleteResponse)
async def delete_role(
    role_id: uuid.UUID,
    _: User = Depends(require_permission("roles", "delete")),
    service: RBACService = Depends(get_rbac_service),
):
    """Delete a custom role."""
    await service.delete_role(role_id)
    return DeleteResponse(id=role_id)


@router.post("/{role_id}/assign", response_model=SuccessResponse)
async def assign_role(
    role_id: uuid.UUID,
    data: RoleAssignment,
    _: User = Depends(require_permission("roles", "assign")),
    service: RBACService = Depends(get_rbac_service),
):
    """Assign a role to a user."""
    await service.assign_role(data.user_id, role_id)
    return SuccessResponse(message="Role assigned successfully")


@router.delete("/{role_id}/unassign/{user_id}", response_model=SuccessResponse)
async def unassign_role(
    role_id: uuid.UUID,
    user_id: uuid.UUID,
    _: User = Depends(require_permission("roles", "assign")),
    service: RBACService = Depends(get_rbac_service),
):
    """Remove a role from a user."""
    await service.unassign_role(user_id, role_id)
    return SuccessResponse(message="Role unassigned successfully")
