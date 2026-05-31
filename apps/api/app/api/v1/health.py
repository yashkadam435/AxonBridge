"""
AxonBridge — Health Check Routes
"""

import time

from fastapi import APIRouter

from app.core.database import check_db_health
from app.core.minio_client import check_minio_health
from app.core.redis import check_redis_health
from app.core.config import get_settings
from app.schemas.common import HealthCheck

router = APIRouter(prefix="/health", tags=["Health"])

_start_time = time.time()
settings = get_settings()


@router.get("", response_model=HealthCheck)
async def health_check():
    """Full system health check."""
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    minio_ok = await check_minio_health()

    all_ok = db_ok and redis_ok and minio_ok
    status = "healthy" if all_ok else ("degraded" if db_ok else "unhealthy")

    return HealthCheck(
        status=status,
        version=settings.APP_VERSION,
        uptime_seconds=round(time.time() - _start_time, 2),
        checks={
            "database": db_ok,
            "redis": redis_ok,
            "minio": minio_ok,
        },
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    db_ok = await check_db_health()
    if not db_ok:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "database_unavailable"},
        )
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}
