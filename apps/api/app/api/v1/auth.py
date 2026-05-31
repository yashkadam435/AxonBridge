"""
AxonBridge — Auth Routes
"""

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_auth_service, get_current_user, get_token_payload
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate with email/password and optional MFA code."""
    ip = request.client.host if request.client else None
    return await auth_service.login(
        email=data.email,
        password=data.password,
        mfa_code=data.mfa_code,
        ip_address=ip,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh an access token using a valid refresh token."""
    return await auth_service.refresh_token(data.refresh_token)


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    payload: dict = Depends(get_token_payload),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Invalidate the current session and token."""
    await auth_service.logout(payload)
    return SuccessResponse(message="Successfully logged out")


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Initialize MFA setup. Returns TOTP secret and QR code URI."""
    secret, uri = await auth_service.setup_mfa(user.id)
    return MFASetupResponse(
        secret=secret,
        provisioning_uri=uri,
    )


@router.post("/mfa/verify", response_model=SuccessResponse)
async def verify_mfa(
    data: MFAVerifyRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify MFA code and enable MFA for the account."""
    await auth_service.verify_and_enable_mfa(user.id, data.code)
    return SuccessResponse(message="MFA enabled successfully")
