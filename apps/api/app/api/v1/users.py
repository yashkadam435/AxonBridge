"""
AxonBridge — User Routes
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_tenant_id,
    get_current_user,
    get_user_service,
    require_permission,
)
from app.models.user import User
from app.schemas.auth import PasswordChangeRequest
from app.schemas.common import PaginatedResponse, IDResponse, DeleteResponse, SuccessResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=IDResponse, status_code=201)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_permission("users", "create")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    service: UserService = Depends(get_user_service),
):
    """Create a new user within the current tenant."""
    user = await service.create(
        tenant_id=tenant_id,
        data=data,
        created_by=current_user.id,
    )
    return IDResponse(id=user.id, message="User created successfully")


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    _: User = Depends(require_permission("users", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    service: UserService = Depends(get_user_service),
):
    """List users in the current tenant."""
    users, total = await service.list_by_tenant(
        tenant_id=tenant_id, page=page, per_page=per_page, search=search
    )
    items = [UserResponse.model_validate(u) for u in users]
    return PaginatedResponse.create(items=items, total=total, page=page, per_page=per_page)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    """Get the current user's profile."""
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _: User = Depends(require_permission("users", "read")),
    service: UserService = Depends(get_user_service),
):
    """Get a specific user by ID."""
    user = await service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(require_permission("users", "update")),
    service: UserService = Depends(get_user_service),
):
    """Update a user."""
    user = await service.update(user_id, data, updated_by=current_user.id)
    return UserResponse.model_validate(user)


@router.put("/me/password", response_model=SuccessResponse)
async def change_password(
    data: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Change the current user's password."""
    await service.change_password(
        user_id=user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return SuccessResponse(message="Password changed successfully")


@router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(
    user_id: uuid.UUID,
    _: User = Depends(require_permission("users", "delete")),
    service: UserService = Depends(get_user_service),
):
    """Soft delete a user."""
    await service.delete(user_id)
    return DeleteResponse(id=user_id)
