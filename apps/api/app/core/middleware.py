"""
AxonBridge — Middleware

CORS, request tracking, audit logging, tenant context, and
rate limiting middleware for the FastAPI application.
"""

import time
import uuid
from collections.abc import Callable
from typing import Any

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique request ID into every request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Bind request ID to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Store on request state for downstream use
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log request timing for performance monitoring."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log request with timing (exclude health checks to reduce noise)
        if not request.url.path.startswith("/api/v1/health"):
            logger.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                client_ip=request.client.host if request.client else "unknown",
            )

        response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Extract tenant context from JWT token and set on request state.
    Skips public endpoints (health, auth).
    """

    SKIP_PATHS = {"/api/v1/health", "/api/v1/auth/login", "/api/v1/auth/refresh", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip for public endpoints
        if any(request.url.path.startswith(path) for path in self.SKIP_PATHS):
            return await call_next(request)

        # Tenant ID will be extracted from JWT in the auth dependency
        # This middleware just initializes the state
        request.state.tenant_id = None
        return await call_next(request)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Capture audit-relevant information for every mutating request.
    Non-GET requests are logged to the audit system.
    """

    SKIP_PATHS = {"/api/v1/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip non-auditable endpoints
        if any(request.url.path.startswith(path) for path in self.SKIP_PATHS):
            return await call_next(request)

        # Capture request metadata for audit
        request.state.audit_metadata = {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        response = await call_next(request)

        # Log mutating operations (POST, PUT, PATCH, DELETE)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            logger.info(
                "audit_http_mutation",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                client_ip=request.client.host if request.client else "unknown",
            )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"

        # Content Security Policy (restrict resources)
        if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'"
            )

        return response
