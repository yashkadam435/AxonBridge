"""
AxonBridge — User Model

Users with authentication, MFA support, and account security.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantScopedModel


class User(TenantScopedModel):
    """
    System user: clinician, admin, auditor, or agent operator.
    """

    __tablename__ = "users"

    # Identity
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Job title: Dr., Nurse, Admin, etc."
    )
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Encrypted TOTP secret"
    )

    # Security
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Preferences
    language_preference: Mapped[str] = mapped_column(
        String(10), default="en", nullable=False
    )
    theme_preference: Mapped[str] = mapped_column(
        String(20), default="system", nullable=False,
        comment="Theme: light, dark, system"
    )

    # Avatar / profile
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship(  # noqa: F821
        "Tenant", back_populates="users"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(  # noqa: F821
        "UserRole", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"

    @property
    def is_locked(self) -> bool:
        """Check if the account is currently locked."""
        if self.locked_until is None:
            return False
        from datetime import UTC
        return datetime.now(UTC) < self.locked_until
