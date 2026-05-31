"""
AxonBridge — Audit Log Routes
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_audit_service,
    get_current_tenant_id,
    require_permission,
)
from app.models.user import User
from app.schemas.audit import AuditIntegrityCheck, AuditLogQuery, AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse])
async def query_audit_logs(
    user_id: uuid.UUID | None = Query(None),
    action: str | None = Query(None),
    action_category: str | None = Query(None),
    resource_type: str | None = Query(None),
    severity: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    _: User = Depends(require_permission("audit", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    service: AuditService = Depends(get_audit_service),
):
    """Query audit logs with filters."""
    query = AuditLogQuery(
        user_id=user_id,
        action=action,
        action_category=action_category,
        resource_type=resource_type,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page,
    )

    items, total = await service.query(tenant_id, query)
    responses = [AuditLogResponse.model_validate(item) for item in items]
    return PaginatedResponse.create(items=responses, total=total, page=page, per_page=per_page)


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: uuid.UUID,
    _: User = Depends(require_permission("audit", "read")),
    service: AuditService = Depends(get_audit_service),
):
    """Get a specific audit log entry."""
    from sqlalchemy import select
    from app.models.audit import AuditLog
    from app.core.database import async_session_factory

    # Direct query since audit entries are immutable
    async with async_session_factory() as session:
        stmt = select(AuditLog).where(AuditLog.id == log_id)
        result = await session.execute(stmt)
        entry = result.scalar_one_or_none()
        if not entry:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Audit log entry", str(log_id))
        return AuditLogResponse.model_validate(entry)


@router.get("/integrity-check", response_model=AuditIntegrityCheck)
async def check_integrity(
    _: User = Depends(require_permission("audit", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    service: AuditService = Depends(get_audit_service),
):
    """Verify the integrity of the audit log chain."""
    is_valid, count, first_invalid_id = await service.verify_integrity(tenant_id)

    return AuditIntegrityCheck(
        is_valid=is_valid,
        total_entries_checked=count,
        first_invalid_entry_id=first_invalid_id,
        checked_at=datetime.utcnow(),
    )
