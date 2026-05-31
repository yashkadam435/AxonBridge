"""
AxonBridge — Tenant Routes
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_tenant_id,
    get_tenant_service,
    require_permission,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, IDResponse, DeleteResponse
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("", response_model=IDResponse, status_code=201)
async def create_tenant(
    data: TenantCreate,
    _: User = Depends(require_permission("tenants", "create")),
    service: TenantService = Depends(get_tenant_service),
):
    """Create a new tenant (healthcare organization)."""
    tenant = await service.create(data)
    return IDResponse(id=tenant.id, message="Tenant created successfully")


@router.get("", response_model=PaginatedResponse[TenantResponse])
async def list_tenants(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: User = Depends(require_permission("tenants", "read")),
    service: TenantService = Depends(get_tenant_service),
):
    """List all tenants."""
    tenants, total = await service.list_all(page=page, per_page=per_page)
    items = [TenantResponse.model_validate(t) for t in tenants]
    return PaginatedResponse.create(items=items, total=total, page=page, per_page=per_page)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    _: User = Depends(require_permission("tenants", "read")),
    service: TenantService = Depends(get_tenant_service),
):
    """Get a specific tenant."""
    tenant = await service.get_by_id(tenant_id)
    return TenantResponse.model_validate(tenant)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: uuid.UUID,
    data: TenantUpdate,
    _: User = Depends(require_permission("tenants", "update")),
    service: TenantService = Depends(get_tenant_service),
):
    """Update a tenant."""
    tenant = await service.update(tenant_id, data)
    return TenantResponse.model_validate(tenant)


@router.delete("/{tenant_id}", response_model=DeleteResponse)
async def delete_tenant(
    tenant_id: uuid.UUID,
    _: User = Depends(require_permission("tenants", "delete")),
    service: TenantService = Depends(get_tenant_service),
):
    """Soft delete a tenant."""
    await service.delete(tenant_id)
    return DeleteResponse(id=tenant_id)
