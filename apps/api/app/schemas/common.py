"""
AxonBridge — Common Schemas

Shared Pydantic schemas for pagination, error responses, and health checks.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated requests."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, per_page: int) -> "PaginatedResponse[T]":
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )


class ErrorDetail(BaseModel):
    """Individual error detail."""
    field: str | None = None
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error_code: str
    message: str
    details: dict[str, Any] | None = None
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Standard success response."""
    message: str = "Operation successful"
    data: dict[str, Any] | None = None


class HealthCheck(BaseModel):
    """System health check response."""
    status: str = Field(description="Overall status: healthy, degraded, unhealthy")
    version: str
    uptime_seconds: float | None = None
    checks: dict[str, bool] = Field(
        default_factory=dict,
        description="Individual service checks: db, redis, minio"
    )


class IDResponse(BaseModel):
    """Response containing just an ID (for create operations)."""
    id: UUID
    message: str = "Resource created successfully"


class DeleteResponse(BaseModel):
    """Response for delete operations."""
    message: str = "Resource deleted successfully"
    id: UUID | None = None
