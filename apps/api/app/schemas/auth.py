"""
AxonBridge — Auth Schemas

Request/response schemas for authentication endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login credentials."""
    email: EmailStr
    password: str = Field(min_length=1)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=6)


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class MFASetupResponse(BaseModel):
    """MFA enrollment response."""
    secret: str
    provisioning_uri: str
    qr_code_base64: str | None = None


class MFAVerifyRequest(BaseModel):
    """MFA verification request."""
    code: str = Field(min_length=6, max_length=6)


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(min_length=12)
    confirm_password: str = Field(min_length=12)


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""
    sub: str
    tenant_id: str
    roles: list[str] = []
    type: str
    exp: datetime
    jti: str
