"""
AxonBridge — Agent Session Models

Agent session tracking, action logging, and confidence scoring
for the perception & automation engine.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantScopedModel


class AgentSession(TenantScopedModel):
    """
    A browser automation agent session.
    Tracks lifecycle from creation to completion.
    """

    __tablename__ = "agent_sessions"

    # Actor
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    # Workflow
    workflow_execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # HIS Target
    his_target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("his_targets.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Session state
    status: Mapped[str] = mapped_column(
        String(50), default="initializing", nullable=False, index=True,
        comment="Status: initializing, active, paused, waiting_confirmation, completed, failed, aborted"
    )
    mode: Mapped[str] = mapped_column(
        String(50), default="assisted", nullable=False,
        comment="Mode: assisted, automated"
    )

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Browser state
    browser_context: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Current browser state: url, page_title, viewport"
    )

    # Statistics
    total_actions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_actions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_actions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    human_interventions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error tracking
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    actions: Mapped[list["AgentAction"]] = relationship(
        "AgentAction", back_populates="session", lazy="noload",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AgentSession(id={self.id}, status='{self.status}')>"


class AgentAction(TenantScopedModel):
    """
    Individual action performed by an agent within a session.
    Each action may require human approval (HITL).
    """

    __tablename__ = "agent_actions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # Action details
    action_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: navigate, click, fill, extract, screenshot, validate, wait"
    )
    action_description: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Human-readable description of the action"
    )

    # Target element
    target_element: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Element being interacted with"
    )
    target_selector: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="CSS/XPath selector used"
    )

    # Parameters & result
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Action result/extracted data"
    )
    result_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False,
        comment="Status: pending, success, failure, skipped"
    )

    # Screenshot
    screenshot_before_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    screenshot_after_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Confidence
    confidence_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="AI confidence in this action (0.0 - 1.0)"
    )

    # Human-in-the-loop
    requires_human_approval: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    human_decision: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Decision: approved, modified, rejected, null (pending/not required)"
    )
    human_decision_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    human_decision_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    human_modification: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="If modified, what changes the human made"
    )

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    session: Mapped["AgentSession"] = relationship(
        "AgentSession", back_populates="actions"
    )

    def __repr__(self) -> str:
        return f"<AgentAction(id={self.id}, type='{self.action_type}', status='{self.result_status}')>"
