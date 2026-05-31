"""
AxonBridge — Tenant Model

Multi-tenancy: each healthcare organization is a tenant with
isolated data, configuration, and HIS connections.
"""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Tenant(BaseModel):
    """
    Healthcare organization (hospital, clinic, health system).
    Top-level entity for data isolation.
    """

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Subscription & status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscription_tier: Mapped[str] = mapped_column(
        String(50), default="standard", nullable=False
    )

    # Tenant-specific configuration
    config: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False,
        comment="Tenant configuration: HIS systems, language defaults, compliance region, etc.",
    )

    # Compliance & data residency
    compliance_region: Mapped[str] = mapped_column(
        String(50),
        default="us",
        nullable=False,
        comment="Data residency: us, eu, in, ae, uk, sg",
    )

    # Contact information
    admin_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User", back_populates="tenant", lazy="selectin"
    )
    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        "Role", back_populates="tenant", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name='{self.name}', slug='{self.slug}')>"
