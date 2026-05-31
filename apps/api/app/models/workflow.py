"""
AxonBridge — Workflow Models

Workflow templates, steps, and execution tracking
for both assisted and automated modes.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TenantScopedModel


class WorkflowTemplate(TenantScopedModel):
    """
    Reusable workflow template defining a series of automated steps.
    Can be in 'assisted' (human confirms each step) or 'automated' mode.
    """

    __tablename__ = "workflow_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(100), default="general", nullable=False,
        comment="Category: clinical, administrative, billing, registration, reporting"
    )

    # Target HIS
    his_target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("his_targets.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Mode
    mode: Mapped[str] = mapped_column(
        String(50), default="assisted", nullable=False,
        comment="Mode: assisted (human confirms), automated (runs autonomously)"
    )
    risk_level: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False,
        comment="Risk: low, medium, high, critical"
    )

    # Configuration
    steps_config: Mapped[dict] = mapped_column(
        JSONB, default=list, nullable=False,
        comment="Ordered list of workflow step configurations"
    )
    trigger_config: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Trigger: manual, scheduled, event-based"
    )
    retry_config: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default='{"max_retries": 3, "backoff_seconds": 5}',
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    steps: Mapped[list["WorkflowStep"]] = relationship(
        "WorkflowStep", back_populates="template", lazy="selectin",
        cascade="all, delete-orphan", order_by="WorkflowStep.step_order",
    )
    executions: Mapped[list["WorkflowExecution"]] = relationship(
        "WorkflowExecution", back_populates="template", lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<WorkflowTemplate(id={self.id}, name='{self.name}', mode='{self.mode}')>"


class WorkflowStep(TenantScopedModel):
    """Individual step within a workflow template."""

    __tablename__ = "workflow_steps"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Step definition
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Action
    action_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: navigate, click, fill, extract, validate, wait, screenshot, conditional"
    )
    parameters: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False,
        comment="Step-specific parameters"
    )

    # Human-in-the-loop
    requires_confirmation: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="If true, agent pauses and waits for human confirmation"
    )
    confirmation_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Message shown to human during confirmation"
    )

    # Error handling
    on_failure: Mapped[str] = mapped_column(
        String(50), default="abort", nullable=False,
        comment="Failure action: abort, retry, skip, fallback"
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )

    # Relationships
    template: Mapped["WorkflowTemplate"] = relationship(
        "WorkflowTemplate", back_populates="steps"
    )

    def __repr__(self) -> str:
        return f"<WorkflowStep(order={self.step_order}, name='{self.name}')>"


class WorkflowExecution(TenantScopedModel):
    """
    Record of a workflow execution instance.
    Tracks status, timing, and results.
    """

    __tablename__ = "workflow_executions"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    initiated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False, index=True,
        comment="Status: pending, running, paused, completed, failed, aborted"
    )
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Results
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_log: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Agent session
    agent_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Relationships
    template: Mapped["WorkflowTemplate"] = relationship(
        "WorkflowTemplate", back_populates="executions"
    )

    def __repr__(self) -> str:
        return f"<WorkflowExecution(id={self.id}, status='{self.status}')>"
