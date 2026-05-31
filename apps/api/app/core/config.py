"""
AxonBridge — Application Configuration

Pydantic Settings for environment-based configuration with HIPAA-compliant defaults.
All sensitive values loaded from environment variables or .env file.
"""

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- Application ----------
    APP_NAME: str = "AxonBridge"
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # ---------- Database ----------
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "axonbridge"
    POSTGRES_USER: str = "axonbridge"
    POSTGRES_PASSWORD: str = "changeme"
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str, info: Any) -> str:
        if v:
            return v
        data = info.data
        return (
            f"postgresql+asyncpg://{data.get('POSTGRES_USER', 'axonbridge')}"
            f":{data.get('POSTGRES_PASSWORD', 'changeme')}"
            f"@{data.get('POSTGRES_HOST', 'localhost')}"
            f":{data.get('POSTGRES_PORT', 5432)}"
            f"/{data.get('POSTGRES_DB', 'axonbridge')}"
        )

    # Database pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # ---------- Redis ----------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = ""
    REDIS_DB: int = 0

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str, info: Any) -> str:
        if v:
            return v
        data = info.data
        password = data.get("REDIS_PASSWORD", "")
        host = data.get("REDIS_HOST", "localhost")
        port = data.get("REDIS_PORT", 6379)
        db = data.get("REDIS_DB", 0)
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    # ---------- MinIO ----------
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "axonbridge_minio"
    MINIO_SECRET_KEY: str = "changeme_minio"
    MINIO_BUCKET_SCREENSHOTS: str = "axonbridge-screenshots"
    MINIO_BUCKET_DOCUMENTS: str = "axonbridge-documents"
    MINIO_USE_SSL: bool = False

    # ---------- JWT ----------
    JWT_SECRET_KEY: str = "changeme_jwt_secret_min_32_chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------- Encryption ----------
    ENCRYPTION_KEY: str = "changeme_32_byte_encryption_key!"
    ENCRYPTION_KEY_ROTATION_DAYS: int = 90

    # ---------- Security ----------
    CORS_ORIGINS: str = "http://localhost:3000"
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 12
    MFA_ISSUER: str = "AxonBridge"

    # ---------- Audit ----------
    AUDIT_LOG_RETENTION_YEARS: int = 7

    # ---------- Logging ----------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ---------- LLM Providers ----------
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
