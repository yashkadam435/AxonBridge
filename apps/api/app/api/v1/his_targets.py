"""
AxonBridge — HIS Target Routes
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, IDResponse, DeleteResponse

# Assuming schemas and services will be implemented in future phases for full functionality
# For now, these are stubbed to satisfy Phase 2 endpoints

router = APIRouter(prefix="/his-targets", tags=["HIS Targets"])

@router.get("", response_model=PaginatedResponse[dict])
async def list_his_targets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: User = Depends(require_permission("system_config", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """List HIS targets for the current tenant."""
    return PaginatedResponse.create(items=[], total=0, page=page, per_page=per_page)

@router.post("", response_model=IDResponse, status_code=201)
async def create_his_target(
    data: dict,
    current_user: User = Depends(require_permission("system_config", "create")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Create a new HIS target."""
    new_id = uuid.uuid4()
    return IDResponse(id=new_id, message="HIS Target created successfully")

@router.get("/{target_id}", response_model=dict)
async def get_his_target(
    target_id: uuid.UUID,
    _: User = Depends(require_permission("system_config", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Get a specific HIS target by ID."""
    return {"id": str(target_id), "name": "Mock HIS"}

@router.delete("/{target_id}", response_model=DeleteResponse)
async def delete_his_target(
    target_id: uuid.UUID,
    _: User = Depends(require_permission("system_config", "delete")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Soft delete a HIS target."""
    return DeleteResponse(id=target_id)
