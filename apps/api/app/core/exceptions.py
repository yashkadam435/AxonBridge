"""
AxonBridge — Custom Exceptions

Exception hierarchy for the application with PHI-safe error messages.
Global exception handlers return standardized error responses.
"""

from typing import Any


class AxonBridgeError(Exception):
    """Base exception for all AxonBridge errors."""

    def __init__(
        self,
        message: str = "An internal error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AxonBridgeError):
    """Authentication failure (invalid credentials, expired token, etc.)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTH_FAILED",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
            details=details,
        )


class AuthorizationError(AxonBridgeError):
    """Authorization failure (insufficient permissions)."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
            details=details,
        )


class NotFoundError(AxonBridgeError):
    """Resource not found."""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str = "",
        details: dict[str, Any] | None = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class ConflictError(AxonBridgeError):
    """Resource conflict (duplicate, already exists)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
            details=details,
        )


class ValidationError(AxonBridgeError):
    """Input validation failure."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: list[dict[str, Any]] | None = None,
        details: dict[str, Any] | None = None,
    ):
        if details is None:
            details = {}
        if errors:
            details["validation_errors"] = errors
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class RateLimitError(AxonBridgeError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: int = 60,
        details: dict[str, Any] | None = None,
    ):
        if details is None:
            details = {}
        details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class HISConnectionError(AxonBridgeError):
    """Failed to connect to or interact with a HIS system."""

    def __init__(
        self,
        his_name: str = "Unknown HIS",
        message: str = "HIS connection failed",
        details: dict[str, Any] | None = None,
    ):
        if details is None:
            details = {}
        details["his_system"] = his_name
        super().__init__(
            message=message,
            status_code=502,
            error_code="HIS_CONNECTION_ERROR",
            details=details,
        )


class EncryptionError(AxonBridgeError):
    """Encryption or decryption failure."""

    def __init__(
        self,
        message: str = "Encryption operation failed",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="ENCRYPTION_ERROR",
            details=details,
        )


class AccountLockedError(AuthenticationError):
    """Account has been locked due to too many failed attempts."""

    def __init__(
        self,
        lockout_minutes: int = 15,
        details: dict[str, Any] | None = None,
    ):
        if details is None:
            details = {}
        details["lockout_minutes"] = lockout_minutes
        super().__init__(
            message=f"Account locked due to too many failed attempts. Try again in {lockout_minutes} minutes.",
            error_code="ACCOUNT_LOCKED",
            details=details,
        )
