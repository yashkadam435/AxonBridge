"""
AxonBridge — Audit Log Models

Immutable, tamper-evident audit logs with chain hashing.
Every agent action, human decision, and data access is recorded.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TenantScopedModel


class AuditLog(TenantScopedModel):
    """
    Immutable audit log entry. No UPDATE or DELETE operations allowed.
    Chain hashing: each entry includes SHA-256 hash of previous entry.
    
    Retention: 7 years (configurable per compliance region).
    """

    __tablename__ = "audit_logs"

    # Actor
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True,
        comment="User who performed the action (null for system actions)"
    )
    agent_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True,
        comment="Agent session if action was performed by an agent"
    )

    # Action
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Action: create, read, update, delete, login, logout, execute, approve, reject, export"
    )
    action_category: Mapped[str] = mapped_column(
        String(50), default="system", nullable=False,
        comment="Category: auth, clinical, workflow, admin, agent, compliance"
    )

    # Target
    resource_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
        comment="Resource: user, tenant, workflow, clinical_note, agent_session, etc."
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="ID of the affected resource"
    )

    # Details
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Additional details (PHI-free)"
    )
    previous_state: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="State before change (for update/delete)"
    )

    # Request context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Integrity
    integrity_hash: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="SHA-256 chain hash for tamper detection"
    )
    previous_hash: Mapped[str] = mapped_column(
        String(64), default="genesis", nullable=False,
        comment="Hash of the previous audit log entry"
    )

    # Timestamp (explicit for querying)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Screenshot reference (for agent actions)
    screenshot_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Severity
    severity: Mapped[str] = mapped_column(
        String(20), default="info", nullable=False,
        comment="Severity: info, warning, critical"
    )

    __table_args__ = (
        Index("ix_audit_logs_tenant_timestamp", "tenant_id", "timestamp"),
        Index("ix_audit_logs_user_action", "user_id", "action"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"
