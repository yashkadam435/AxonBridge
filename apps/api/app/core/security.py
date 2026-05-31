"""
AxonBridge — Security Utilities

JWT token management, password hashing, AES-256-GCM field encryption,
MFA (TOTP) support, and API key generation.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import pyotp
from cryptography.fernet import Fernet
import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

# ---------- Password Hashing ----------

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def validate_password_strength(password: str) -> list[str]:
    """
    Validate password meets security requirements.
    Returns list of validation errors (empty if valid).
    """
    errors: list[str] = []
    min_length = settings.PASSWORD_MIN_LENGTH

    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")

    return errors


# ---------- JWT Tokens ----------


def create_access_token(
    subject: str,
    tenant_id: str,
    roles: list[str] | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT access token."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "roles": roles or [],
        "type": "access",
        "iat": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, tenant_id: str) -> str:
    """Create a JWT refresh token with longer expiry."""
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "type": "refresh",
        "iat": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """Verify the token is of the expected type (access/refresh)."""
    return payload.get("type") == expected_type


# ---------- AES-256 Field Encryption ----------

# Derive a Fernet key from the encryption key setting
def _derive_fernet_key(key: str) -> bytes:
    """Derive a Fernet-compatible key from the app encryption key."""
    import base64
    # SHA-256 hash to get exactly 32 bytes, then base64 encode for Fernet
    key_bytes = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


_fernet = Fernet(_derive_fernet_key(settings.ENCRYPTION_KEY))


def encrypt_field(value: str) -> str:
    """Encrypt a string value using AES-256 (Fernet). Returns base64 string."""
    if not value:
        return value
    return _fernet.encrypt(value.encode()).decode()


def decrypt_field(encrypted_value: str) -> str:
    """Decrypt a Fernet-encrypted string."""
    if not encrypted_value:
        return encrypted_value
    return _fernet.decrypt(encrypted_value.encode()).decode()


# ---------- MFA (TOTP) ----------


def generate_mfa_secret() -> str:
    """Generate a new TOTP secret for MFA enrollment."""
    return pyotp.random_base32()


def get_mfa_provisioning_uri(secret: str, email: str) -> str:
    """Generate a provisioning URI for QR code display."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.MFA_ISSUER)


def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify a TOTP code against the secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


# ---------- API Keys ----------


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"axb_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


# ---------- Audit Integrity ----------


def compute_chain_hash(previous_hash: str, log_data: str) -> str:
    """
    Compute a chain hash for audit log integrity.
    Each entry's hash includes the previous entry's hash,
    creating a tamper-evident chain.
    """
    combined = f"{previous_hash}:{log_data}"
    return hashlib.sha256(combined.encode()).hexdigest()
