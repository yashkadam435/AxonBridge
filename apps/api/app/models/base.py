"""
AxonBridge — Base Model

Base SQLAlchemy model with UUID primary key, audit timestamps,
soft delete, and multi-tenancy support.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditMixin:
    """Mixin that adds audit timestamp fields to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=text("NOW()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=text("NOW()"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete support."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("FALSE"),
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class TenantMixin:
    """Mixin that adds multi-tenancy support via tenant_id."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class BaseModel(Base, AuditMixin, SoftDeleteMixin):
    """
    Abstract base model for all AxonBridge entities.
    
    Provides:
    - UUID primary key
    - created_at, updated_at timestamps
    - created_by, updated_by user references
    - is_deleted soft delete flag
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )


class TenantScopedModel(BaseModel, TenantMixin):
    """
    Abstract base model for tenant-scoped entities.
    Adds tenant_id for multi-tenancy data isolation.
    """

    __abstract__ = True
