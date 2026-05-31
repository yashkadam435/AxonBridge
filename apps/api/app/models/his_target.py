"""
AxonBridge — HIS Target Models

Configuration for target Hospital Information Systems
that AxonBridge connects to via UI automation.
"""

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantScopedModel


class HISTarget(TenantScopedModel):
    """
    A target HIS/EHR system that AxonBridge automates against.
    Stores connection config, auth, and health status.
    """

    __tablename__ = "his_targets"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Connection
    his_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: web, desktop, hybrid"
    )
    base_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="Base URL for web-based HIS"
    )
    application_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="Executable path for desktop HIS"
    )

    # Authentication for HIS (encrypted)
    auth_config: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Encrypted auth config: {type, username_encrypted, password_encrypted, ...}"
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False,
        comment="Status: pending, active, inactive, error"
    )
    last_health_check: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    health_check_interval_seconds: Mapped[int] = mapped_column(
        Integer, default=300, nullable=False
    )

    # Browser automation config
    browser_config: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default="{}", nullable=False,
        comment="Playwright config: viewport, user_agent, proxy, etc."
    )

    # Element mapping
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    element_maps: Mapped[list["HISElementMap"]] = relationship(
        "HISElementMap", back_populates="his_target", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<HISTarget(id={self.id}, name='{self.name}', type='{self.his_type}')>"


class HISElementMap(TenantScopedModel):
    """
    Mapping of UI elements within a HIS system.
    Used by the perception engine to locate and interact with elements.
    Supports multiple selector strategies for resilience.
    """

    __tablename__ = "his_element_maps"

    his_target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("his_targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Element identification
    element_name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Human-readable element name: 'Patient Name Input', 'Save Button'"
    )
    element_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: input, button, link, select, table, text, container"
    )
    page_context: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Page/screen where this element appears"
    )

    # Selector strategies (ordered by priority)
    selectors: Mapped[dict] = mapped_column(
        JSONB, nullable=False,
        comment="Selectors: {accessibility: ..., css: ..., xpath: ..., text: ..., visual: ...}"
    )

    # Verification
    last_verified: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_screenshot_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Relationships
    his_target: Mapped["HISTarget"] = relationship(
        "HISTarget", back_populates="element_maps"
    )

    def __repr__(self) -> str:
        return f"<HISElementMap(id={self.id}, name='{self.element_name}')>"
