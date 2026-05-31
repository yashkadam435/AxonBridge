"""
AxonBridge — Tenant Service

Tenant CRUD with slug generation and default role seeding.
"""

import uuid

from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.role import Role, Permission, RolePermission, DEFAULT_ROLES, DEFAULT_PERMISSIONS
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate

logger = get_logger(__name__)


class TenantService:
    """Tenant management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: TenantCreate) -> Tenant:
        """Create a new tenant with default roles and permissions."""
        # Generate unique slug
        slug = slugify(data.name)
        existing = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        if existing.scalar_one_or_none():
            slug = f"{slug}-{str(uuid.uuid4())[:8]}"

        tenant = Tenant(
            name=data.name,
            slug=slug,
            description=data.description,
            admin_email=data.admin_email,
            admin_phone=data.admin_phone,
            subscription_tier=data.subscription_tier,
            compliance_region=data.compliance_region,
            config=data.config,
        )
        self.db.add(tenant)
        await self.db.flush()

        # Seed default roles
        await self._seed_default_roles(tenant.id)

        logger.info("tenant_created", tenant_id=str(tenant.id), name=data.name)
        return tenant

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant:
        """Get a tenant by ID."""
        stmt = select(Tenant).where(
            Tenant.id == tenant_id,
            Tenant.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(stmt)
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise NotFoundError("Tenant", str(tenant_id))
        return tenant

    async def get_by_slug(self, slug: str) -> Tenant:
        """Get a tenant by slug."""
        stmt = select(Tenant).where(Tenant.slug == slug, Tenant.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise NotFoundError("Tenant", slug)
        return tenant

    async def list_all(
        self, page: int = 1, per_page: int = 20
    ) -> tuple[list[Tenant], int]:
        """List all tenants with pagination."""
        stmt = select(Tenant).where(Tenant.is_deleted == False)  # noqa: E712

        # Count
        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar() or 0

        # Paginate
        offset = (page - 1) * per_page
        stmt = stmt.order_by(Tenant.created_at.desc()).offset(offset).limit(per_page)
        result = await self.db.execute(stmt)
        tenants = list(result.scalars().all())

        return tenants, total

    async def update(self, tenant_id: uuid.UUID, data: TenantUpdate) -> Tenant:
        """Update a tenant."""
        tenant = await self.get_by_id(tenant_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tenant, field, value)

        await self.db.flush()
        logger.info("tenant_updated", tenant_id=str(tenant_id))
        return tenant

    async def delete(self, tenant_id: uuid.UUID) -> None:
        """Soft delete a tenant."""
        tenant = await self.get_by_id(tenant_id)
        tenant.is_deleted = True
        tenant.is_active = False
        from datetime import UTC, datetime
        tenant.deleted_at = datetime.now(UTC)
        await self.db.flush()
        logger.info("tenant_deleted", tenant_id=str(tenant_id))

    async def _seed_default_roles(self, tenant_id: uuid.UUID) -> None:
        """Create default system roles for a new tenant."""
        # Ensure global permissions exist
        permissions = await self._ensure_permissions()

        for role_data in DEFAULT_ROLES:
            role = Role(
                tenant_id=tenant_id,
                name=role_data["name"],
                description=role_data["description"],
                priority=role_data["priority"],
                is_system_role=True,
            )
            self.db.add(role)
            await self.db.flush()

            # Assign permissions based on role
            role_perms = self._get_role_permissions(role_data["name"], permissions)
            for perm in role_perms:
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)

        await self.db.flush()
        logger.info("default_roles_seeded", tenant_id=str(tenant_id))

    async def _ensure_permissions(self) -> list[Permission]:
        """Ensure all default permissions exist in the database."""
        permissions = []
        for resource, action, description in DEFAULT_PERMISSIONS:
            stmt = select(Permission).where(
                Permission.resource == resource,
                Permission.action == action,
            )
            result = await self.db.execute(stmt)
            perm = result.scalar_one_or_none()

            if not perm:
                perm = Permission(
                    resource=resource,
                    action=action,
                    description=description,
                )
                self.db.add(perm)
                await self.db.flush()

            permissions.append(perm)
        return permissions

    def _get_role_permissions(
        self, role_name: str, all_permissions: list[Permission]
    ) -> list[Permission]:
        """Determine which permissions a role should have."""
        perm_map = {f"{p.resource}:{p.action}": p for p in all_permissions}

        if role_name == "system_admin":
            return all_permissions  # Full access

        if role_name == "admin":
            excluded = {"tenants:create", "tenants:delete"}
            return [p for key, p in perm_map.items() if key not in excluded]

        if role_name == "clinician":
            allowed_prefixes = {"clinical:", "workflows:read", "workflows:execute", "agents:read"}
            return [
                p for key, p in perm_map.items()
                if any(key.startswith(prefix) or key == prefix for prefix in allowed_prefixes)
            ]

        if role_name == "agent_operator":
            allowed_prefixes = {"agents:", "workflows:", "settings:read"}
            return [
                p for key, p in perm_map.items()
                if any(key.startswith(prefix) for prefix in allowed_prefixes)
            ]

        if role_name == "auditor":
            allowed = {"audit:read", "audit:export", "users:read", "workflows:read", "agents:read"}
            return [p for key, p in perm_map.items() if key in allowed]

        return []
