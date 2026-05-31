"""
AxonBridge — API v1 Router

Aggregates all v1 route modules.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    health,
    users,
    roles,
    tenants,
    audit,
    his_targets,
    workflows,
    clinical
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(audit.router)
api_router.include_router(his_targets.router)
api_router.include_router(workflows.router)
api_router.include_router(clinical.router)
