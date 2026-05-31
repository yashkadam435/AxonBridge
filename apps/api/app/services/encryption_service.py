"""
AxonBridge — Encryption Service

AES-256-GCM field-level encryption for PHI data.
Supports key rotation and encrypted SQLAlchemy column type.
"""

from app.core.security import encrypt_field, decrypt_field
from app.core.logging import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting PHI fields."""

    @staticmethod
    def encrypt(value: str | None) -> str | None:
        """Encrypt a value. Returns None if input is None."""
        if value is None:
            return None
        try:
            return encrypt_field(value)
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise

    @staticmethod
    def decrypt(value: str | None) -> str | None:
        """Decrypt a value. Returns None if input is None."""
        if value is None:
            return None
        try:
            return decrypt_field(value)
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise

    @staticmethod
    def encrypt_dict(data: dict, fields: list[str]) -> dict:
        """Encrypt specific fields in a dictionary."""
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field] is not None:
                encrypted[field] = encrypt_field(str(encrypted[field]))
        return encrypted

    @staticmethod
    def decrypt_dict(data: dict, fields: list[str]) -> dict:
        """Decrypt specific fields in a dictionary."""
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field] is not None:
                decrypted[field] = decrypt_field(decrypted[field])
        return decrypted
