"""
AxonBridge — RBAC Service

Role and permission management with caching.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.role import Permission, Role, RolePermission, UserRole
from app.schemas.role import RoleCreate, RoleUpdate

logger = get_logger(__name__)


class RBACService:
    """Role-Based Access Control service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------- Permission Checking ----------

    async def check_permission(
        self,
        user_id: uuid.UUID,
        resource: str,
        action: str,
    ) -> bool:
        """
        Check if a user has a specific permission.
        Returns True if authorized, raises AuthorizationError otherwise.
        """
        permissions = await self.get_user_permissions(user_id)
        permission_key = f"{resource}:{action}"

        if permission_key in permissions:
            return True

        # Check wildcard permissions
        if f"{resource}:*" in permissions or "*:*" in permissions:
            return True

        raise AuthorizationError(
            message=f"Permission denied: {resource}:{action}",
            details={"required_permission": permission_key},
        )

    async def get_user_permissions(self, user_id: uuid.UUID) -> set[str]:
        """Get all permission keys for a user."""
        stmt = (
            select(Permission.resource, Permission.action)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return {f"{row.resource}:{row.action}" for row in result.all()}

    async def get_user_roles(self, user_id: uuid.UUID) -> list[Role]:
        """Get all roles for a user."""
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ---------- Role CRUD ----------

    async def create_role(
        self, tenant_id: uuid.UUID, data: RoleCreate
    ) -> Role:
        """Create a new custom role."""
        # Check for duplicate name
        existing = await self.db.execute(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.name == data.name,
                Role.is_deleted == False,  # noqa: E712
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"Role '{data.name}' already exists")

        role = Role(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            priority=data.priority,
            is_system_role=False,
        )
        self.db.add(role)
        await self.db.flush()

        # Assign permissions
        for perm_id in data.permission_ids:
            rp = RolePermission(role_id=role.id, permission_id=perm_id)
            self.db.add(rp)

        await self.db.flush()
        logger.info("role_created", role_id=str(role.id), name=data.name)
        return role

    async def get_role(self, role_id: uuid.UUID) -> Role:
        """Get a role by ID."""
        stmt = select(Role).where(Role.id == role_id, Role.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise NotFoundError("Role", str(role_id))
        return role

    async def list_roles(self, tenant_id: uuid.UUID) -> list[Role]:
        """List all roles for a tenant."""
        stmt = (
            select(Role)
            .where(Role.tenant_id == tenant_id, Role.is_deleted == False)  # noqa: E712
            .order_by(Role.priority.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_role(self, role_id: uuid.UUID, data: RoleUpdate) -> Role:
        """Update a role (system roles cannot be modified)."""
        role = await self.get_role(role_id)
        if role.is_system_role:
            raise ValidationError(message="System roles cannot be modified")

        update_data = data.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)

        for field, value in update_data.items():
            setattr(role, field, value)

        # Update permissions if provided
        if permission_ids is not None:
            # Remove existing permissions
            existing = await self.db.execute(
                select(RolePermission).where(RolePermission.role_id == role_id)
            )
            for rp in existing.scalars().all():
                await self.db.delete(rp)

            # Add new permissions
            for perm_id in permission_ids:
                rp = RolePermission(role_id=role.id, permission_id=perm_id)
                self.db.add(rp)

        await self.db.flush()
        logger.info("role_updated", role_id=str(role_id))
        return role

    async def delete_role(self, role_id: uuid.UUID) -> None:
        """Delete a role (system roles cannot be deleted)."""
        role = await self.get_role(role_id)
        if role.is_system_role:
            raise ValidationError(message="System roles cannot be deleted")

        role.is_deleted = True
        from datetime import UTC, datetime
        role.deleted_at = datetime.now(UTC)
        await self.db.flush()
        logger.info("role_deleted", role_id=str(role_id))

    # ---------- Role Assignment ----------

    async def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        """Assign a role to a user."""
        # Check if already assigned
        existing = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Role already assigned to user")

        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.flush()
        logger.info("role_assigned", user_id=str(user_id), role_id=str(role_id))

    async def unassign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        """Remove a role from a user."""
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = await self.db.execute(stmt)
        user_role = result.scalar_one_or_none()
        if not user_role:
            raise NotFoundError("Role assignment")

        await self.db.delete(user_role)
        await self.db.flush()
        logger.info("role_unassigned", user_id=str(user_id), role_id=str(role_id))

    # ---------- Permissions ----------

    async def list_permissions(self) -> list[Permission]:
        """List all available permissions."""
        stmt = select(Permission).where(Permission.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
