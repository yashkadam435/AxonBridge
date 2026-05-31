"""
AxonBridge — RBAC Models

Role-Based Access Control with granular permissions.
Default roles: system_admin, clinician, admin, auditor, agent.
"""

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantScopedModel, BaseModel


class Role(TenantScopedModel):
    """
    Role definition for RBAC.
    System roles cannot be modified or deleted.
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="System roles are immutable and cannot be deleted"
    )
    priority: Mapped[int] = mapped_column(
        default=0, nullable=False,
        comment="Higher priority = more access. Used for role hierarchy."
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(  # noqa: F821
        "Tenant", back_populates="roles"
    )
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", lazy="selectin", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_role_tenant_name"),
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(BaseModel):
    """
    Permission definition: resource + action pairs.
    Example: ("users", "read"), ("workflows", "execute"), ("audit", "read")
    """

    __tablename__ = "permissions"

    resource: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Resource: users, tenants, workflows, clinical, audit, agents, settings"
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Action: create, read, update, delete, execute, export"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Optional conditions: e.g., {own_records_only: true}"
    )

    # Relationships
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permission_resource_action"),
    )

    def __repr__(self) -> str:
        return f"<Permission(resource='{self.resource}', action='{self.action}')>"


class UserRole(BaseModel):
    """Many-to-many: User ↔ Role assignment."""

    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="user_roles"
    )
    role: Mapped["Role"] = relationship(
        "Role", back_populates="user_roles"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )


class RolePermission(BaseModel):
    """Many-to-many: Role ↔ Permission assignment."""

    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    role: Mapped["Role"] = relationship(
        "Role", back_populates="role_permissions"
    )
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_permissions"
    )

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


# ---------- Default System Roles ----------

DEFAULT_ROLES = [
    {
        "name": "system_admin",
        "description": "Full system access. Can manage tenants, users, and all configurations.",
        "priority": 100,
    },
    {
        "name": "admin",
        "description": "Tenant administrator. Can manage users, roles, workflows, and settings within their tenant.",
        "priority": 80,
    },
    {
        "name": "clinician",
        "description": "Clinical user. Can use clinical documentation, view patient data, and manage encounters.",
        "priority": 60,
    },
    {
        "name": "agent_operator",
        "description": "Can configure and monitor automation agents and workflows.",
        "priority": 50,
    },
    {
        "name": "auditor",
        "description": "Read-only access to audit logs, compliance reports, and system activity.",
        "priority": 40,
    },
]

DEFAULT_PERMISSIONS = [
    # Users
    ("users", "create", "Create new users"),
    ("users", "read", "View user profiles"),
    ("users", "update", "Modify user information"),
    ("users", "delete", "Deactivate users"),
    # Tenants
    ("tenants", "create", "Create new tenants"),
    ("tenants", "read", "View tenant information"),
    ("tenants", "update", "Modify tenant settings"),
    ("tenants", "delete", "Deactivate tenants"),
    # Workflows
    ("workflows", "create", "Create workflow templates"),
    ("workflows", "read", "View workflows"),
    ("workflows", "update", "Modify workflows"),
    ("workflows", "delete", "Delete workflows"),
    ("workflows", "execute", "Execute workflows"),
    # Clinical
    ("clinical", "create", "Create clinical notes and encounters"),
    ("clinical", "read", "View clinical data"),
    ("clinical", "update", "Modify clinical records"),
    ("clinical", "export", "Export clinical data"),
    # Agents
    ("agents", "create", "Create agent sessions"),
    ("agents", "read", "View agent activity"),
    ("agents", "update", "Configure agents"),
    ("agents", "execute", "Start/stop agents"),
    # Audit
    ("audit", "read", "View audit logs"),
    ("audit", "export", "Export audit data"),
    # Settings
    ("settings", "read", "View system settings"),
    ("settings", "update", "Modify system settings"),
    # Roles
    ("roles", "create", "Create roles"),
    ("roles", "read", "View roles"),
    ("roles", "update", "Modify roles"),
    ("roles", "delete", "Delete roles"),
    ("roles", "assign", "Assign roles to users"),
]
