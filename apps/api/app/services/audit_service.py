"""
AxonBridge — Audit Service

Immutable audit log management with chain hashing for tamper detection.
"""

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import compute_chain_hash
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogQuery

logger = get_logger(__name__)


class AuditService:
    """Service for creating and querying immutable audit logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        tenant_id: uuid.UUID,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: uuid.UUID | None = None,
        agent_session_id: uuid.UUID | None = None,
        description: str | None = None,
        details: dict | None = None,
        previous_state: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str | None = None,
        severity: str = "info",
        action_category: str = "system",
        screenshot_url: str | None = None,
    ) -> AuditLog:
        """
        Create an immutable audit log entry with chain hash.
        """
        now = datetime.now(UTC)

        # Get the hash of the last audit entry for this tenant
        previous_hash = await self._get_last_hash(tenant_id)

        # Build the log data string for hashing
        log_data = json.dumps({
            "tenant_id": str(tenant_id),
            "user_id": str(user_id) if user_id else None,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "timestamp": now.isoformat(),
        }, sort_keys=True)

        # Compute chain hash
        integrity_hash = compute_chain_hash(previous_hash, log_data)

        entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            agent_session_id=agent_session_id,
            action=action,
            action_category=action_category,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=details,
            previous_state=previous_state,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            severity=severity,
            integrity_hash=integrity_hash,
            previous_hash=previous_hash,
            timestamp=now,
            screenshot_url=screenshot_url,
        )

        self.db.add(entry)
        await self.db.flush()

        logger.info(
            "audit_log_created",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=severity,
        )

        return entry

    async def query(
        self,
        tenant_id: uuid.UUID,
        query: AuditLogQuery,
    ) -> tuple[list[AuditLog], int]:
        """Query audit logs with filters and pagination."""
        stmt = select(AuditLog).where(
            AuditLog.tenant_id == tenant_id,
            AuditLog.is_deleted == False,  # noqa: E712
        )

        # Apply filters
        if query.user_id:
            stmt = stmt.where(AuditLog.user_id == query.user_id)
        if query.action:
            stmt = stmt.where(AuditLog.action == query.action)
        if query.action_category:
            stmt = stmt.where(AuditLog.action_category == query.action_category)
        if query.resource_type:
            stmt = stmt.where(AuditLog.resource_type == query.resource_type)
        if query.resource_id:
            stmt = stmt.where(AuditLog.resource_id == query.resource_id)
        if query.severity:
            stmt = stmt.where(AuditLog.severity == query.severity)
        if query.start_date:
            stmt = stmt.where(AuditLog.timestamp >= query.start_date)
        if query.end_date:
            stmt = stmt.where(AuditLog.timestamp <= query.end_date)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply ordering and pagination
        offset = (query.page - 1) * query.per_page
        stmt = stmt.order_by(desc(AuditLog.timestamp)).offset(offset).limit(query.per_page)

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def verify_integrity(self, tenant_id: uuid.UUID) -> tuple[bool, int, uuid.UUID | None]:
        """
        Verify the integrity of the audit log chain for a tenant.
        Returns (is_valid, entries_checked, first_invalid_id).
        """
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.timestamp.asc())
        )
        result = await self.db.execute(stmt)
        entries = list(result.scalars().all())

        if not entries:
            return True, 0, None

        expected_previous_hash = "genesis"

        for entry in entries:
            if entry.previous_hash != expected_previous_hash:
                logger.warning(
                    "audit_integrity_violation",
                    entry_id=str(entry.id),
                    expected_hash=expected_previous_hash,
                    actual_hash=entry.previous_hash,
                )
                return False, entries.index(entry), entry.id

            expected_previous_hash = entry.integrity_hash

        return True, len(entries), None

    async def _get_last_hash(self, tenant_id: uuid.UUID) -> str:
        """Get the hash of the most recent audit entry for a tenant."""
        stmt = (
            select(AuditLog.integrity_hash)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(desc(AuditLog.timestamp))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        last_hash = result.scalar()
        return last_hash or "genesis"
