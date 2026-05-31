"""
AxonBridge — Auth Service

Login, JWT token management, MFA, and session management.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    ValidationError,
)
from app.core.logging import get_logger
from app.core.redis import (
    blacklist_token,
    check_rate_limit,
    invalidate_all_sessions,
    store_session,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_mfa_secret,
    get_mfa_provisioning_uri,
    hash_password,
    validate_password_strength,
    verify_mfa_code,
    verify_password,
    verify_token_type,
)
from app.models.role import UserRole
from app.models.user import User
from app.schemas.auth import TokenResponse

settings = get_settings()
logger = get_logger(__name__)


class AuthService:
    """Authentication and session management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(
        self,
        email: str,
        password: str,
        mfa_code: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """
        Authenticate a user with email/password and optional MFA.
        Implements rate limiting and account lockout.
        """
        # Rate limit check
        allowed, remaining = await check_rate_limit(
            f"login:{email}",
            max_requests=settings.MAX_LOGIN_ATTEMPTS,
            window_seconds=settings.ACCOUNT_LOCKOUT_MINUTES * 60,
        )
        if not allowed:
            raise AccountLockedError(lockout_minutes=settings.ACCOUNT_LOCKOUT_MINUTES)

        # Find user
        stmt = select(User).where(User.email == email, User.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning("login_failed_user_not_found", email=email)
            raise AuthenticationError(message="Invalid email or password")

        # Check if account is locked
        if user.is_locked:
            raise AccountLockedError(lockout_minutes=settings.ACCOUNT_LOCKOUT_MINUTES)

        # Verify password
        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1

            # Lock account after max attempts
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(UTC) + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_MINUTES
                )
                logger.warning("account_locked", user_id=str(user.id), email=email)

            await self.db.flush()
            raise AuthenticationError(message="Invalid email or password")

        # Check if account is active
        if not user.is_active:
            raise AuthenticationError(
                message="Account is deactivated",
                error_code="ACCOUNT_INACTIVE",
            )

        # MFA check
        if user.mfa_enabled:
            if not mfa_code:
                raise AuthenticationError(
                    message="MFA code required",
                    error_code="MFA_REQUIRED",
                )
            if not user.mfa_secret or not verify_mfa_code(user.mfa_secret, mfa_code):
                raise AuthenticationError(
                    message="Invalid MFA code",
                    error_code="MFA_INVALID",
                )

        # Get user roles
        roles = await self._get_user_roles(user.id)

        # Generate tokens
        access_token = create_access_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=roles,
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id),
        )

        # Update login metadata
        user.last_login = datetime.now(UTC)
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.db.flush()

        # Store session in Redis
        session_id = str(uuid.uuid4())
        await store_session(
            user_id=str(user.id),
            session_id=session_id,
            data={"roles": roles, "tenant_id": str(user.tenant_id)},
            ttl_seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        logger.info("login_success", user_id=str(user.id), email=email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Generate new token pair from a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise AuthenticationError(
                message="Invalid refresh token",
                error_code="TOKEN_INVALID",
            )

        if not verify_token_type(payload, "refresh"):
            raise AuthenticationError(
                message="Invalid token type",
                error_code="TOKEN_TYPE_INVALID",
            )

        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        # Verify user still exists and is active
        stmt = select(User).where(
            User.id == uuid.UUID(user_id),
            User.is_active == True,  # noqa: E712
            User.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise AuthenticationError(message="User not found or inactive")

        roles = await self._get_user_roles(user.id)

        new_access = create_access_token(
            subject=str(user.id),
            tenant_id=tenant_id,
            roles=roles,
        )
        new_refresh = create_refresh_token(
            subject=str(user.id),
            tenant_id=tenant_id,
        )

        # Blacklist old refresh token
        jti = payload.get("jti", "")
        exp = payload.get("exp", 0)
        ttl = max(int(exp - datetime.now(UTC).timestamp()), 0)
        if jti and ttl > 0:
            await blacklist_token(jti, ttl)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, token_payload: dict) -> None:
        """Invalidate the current session."""
        user_id = token_payload.get("sub", "")
        jti = token_payload.get("jti", "")

        # Blacklist current access token
        if jti:
            await blacklist_token(jti, settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        # Invalidate all Redis sessions
        await invalidate_all_sessions(user_id)

        logger.info("logout_success", user_id=user_id)

    async def setup_mfa(self, user_id: uuid.UUID) -> tuple[str, str]:
        """
        Set up MFA for a user. Returns (secret, provisioning_uri).
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise AuthenticationError(message="User not found")

        secret = generate_mfa_secret()
        uri = get_mfa_provisioning_uri(secret, user.email)

        # Store the secret (will be confirmed on first verification)
        user.mfa_secret = secret
        await self.db.flush()

        return secret, uri

    async def verify_and_enable_mfa(
        self, user_id: uuid.UUID, code: str
    ) -> bool:
        """Verify MFA code and enable MFA for the user."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None or not user.mfa_secret:
            raise AuthenticationError(message="MFA not set up")

        if not verify_mfa_code(user.mfa_secret, code):
            raise AuthenticationError(
                message="Invalid MFA code",
                error_code="MFA_INVALID",
            )

        user.mfa_enabled = True
        await self.db.flush()

        logger.info("mfa_enabled", user_id=str(user_id))
        return True

    async def _get_user_roles(self, user_id: uuid.UUID) -> list[str]:
        """Get role names for a user."""
        stmt = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        user_roles = result.scalars().all()
        return [ur.role.name for ur in user_roles if ur.role]
