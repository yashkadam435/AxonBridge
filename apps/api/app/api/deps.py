"""
AxonBridge — API Dependencies

FastAPI dependency injection for auth, DB sessions, RBAC, and audit.
"""

import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, Header, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.redis import is_token_blacklisted
from app.core.security import decode_token, verify_token_type
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.rbac_service import RBACService
from app.services.tenant_service import TenantService
from app.services.user_service import UserService


async def get_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AsyncSession, None]:
    """Provide database session dependency."""
    yield session


async def get_token_payload(
    request: Request,
    authorization: str = Header(None),
) -> dict[str, Any]:
    """Extract and validate JWT token from Authorization header."""
    if not authorization:
        raise AuthenticationError(
            message="Missing authorization header",
            error_code="AUTH_HEADER_MISSING",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError(
            message="Invalid authorization scheme. Use: Bearer <token>",
            error_code="AUTH_SCHEME_INVALID",
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise AuthenticationError(
            message="Invalid or expired token",
            error_code="TOKEN_INVALID",
        )

    if not verify_token_type(payload, "access"):
        raise AuthenticationError(
            message="Invalid token type",
            error_code="TOKEN_TYPE_INVALID",
        )

    # Check if token is blacklisted
    jti = payload.get("jti", "")
    if jti and await is_token_blacklisted(jti):
        raise AuthenticationError(
            message="Token has been revoked",
            error_code="TOKEN_REVOKED",
        )

    # Store payload on request state
    request.state.token_payload = payload
    request.state.tenant_id = payload.get("tenant_id")
    request.state.user_id = payload.get("sub")

    return payload


async def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get the currently authenticated user."""
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(message="Invalid token payload")

    from sqlalchemy import select
    stmt = select(User).where(
        User.id == uuid.UUID(user_id),
        User.is_active == True,  # noqa: E712
        User.is_deleted == False,  # noqa: E712
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(message="User not found or inactive")

    return user


async def get_current_tenant_id(
    payload: dict = Depends(get_token_payload),
) -> uuid.UUID:
    """Get the current tenant ID from the JWT token."""
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise AuthenticationError(message="Missing tenant context")
    return uuid.UUID(tenant_id)


def require_permission(resource: str, action: str):
    """
    Factory for permission-checking dependency.
    Usage: Depends(require_permission("users", "create"))
    """
    async def _check(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
    ) -> User:
        rbac = RBACService(db)
        await rbac.check_permission(user.id, resource, action)
        return user

    return _check


# ---------- Service Dependencies ----------


async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
) -> AuthService:
    return AuthService(db)


async def get_tenant_service(
    db: AsyncSession = Depends(get_db_session),
) -> TenantService:
    return TenantService(db)


async def get_user_service(
    db: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(db)


async def get_rbac_service(
    db: AsyncSession = Depends(get_db_session),
) -> RBACService:
    return RBACService(db)


async def get_audit_service(
    db: AsyncSession = Depends(get_db_session),
) -> AuditService:
    return AuditService(db)
