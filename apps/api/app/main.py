"""
AxonBridge — FastAPI Application

Main application entry point with middleware, exception handlers,
and startup/shutdown lifecycle events.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.core.exceptions import AxonBridgeError
from app.core.logging import get_logger, setup_logging
from app.core.middleware import (
    AuditMiddleware,
    RequestIDMiddleware,
    RequestTimingMiddleware,
    SecurityHeadersMiddleware,
    TenantContextMiddleware,
)
from app.core.minio_client import ensure_buckets
from app.core.redis import close_redis

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application startup and shutdown lifecycle."""
    # Startup
    setup_logging()
    logger.info("axonbridge_starting", version=settings.APP_VERSION, env=settings.APP_ENV)

    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))

    try:
        await ensure_buckets()
        logger.info("minio_buckets_initialized")
    except Exception as e:
        logger.warning("minio_init_failed", error=str(e))

    logger.info("axonbridge_started", host=settings.APP_HOST, port=settings.APP_PORT)

    yield

    # Shutdown
    logger.info("axonbridge_shutting_down")
    await close_db()
    await close_redis()
    logger.info("axonbridge_stopped")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="AxonBridge API",
        description=(
            "Universal Agentic Automation Layer for Healthcare — "
            "HIPAA-compliant AI middleware for HIS/EHR systems."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ---------- CORS ----------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
    )

    # ---------- Custom Middleware (order matters: last added = first executed) ----------
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ---------- Exception Handlers ----------
    @app.exception_handler(AxonBridgeError)
    async def axonbridge_error_handler(request: Request, exc: AxonBridgeError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled_exception",
            error=str(exc),
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    # ---------- Routes ----------
    app.include_router(api_router)

    # ---------- Root ----------
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "operational",
            "docs": "/docs" if settings.is_development else None,
        }

    return app


# Application instance
app = create_app()
