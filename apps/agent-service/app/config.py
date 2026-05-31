from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    REDIS_URL: str = "redis://axonbridge-redis:6379/1"
    CORE_API_URL: str = "http://axonbridge-api:8000/api/v1"
    PLAYWRIGHT_HEADLESS: bool = True
    MINIO_ENDPOINT: str = "axonbridge-minio:9000"
    MINIO_ACCESS_KEY: str = "axonbridge_minio"
    MINIO_SECRET_KEY: str = "changeme_minio_secret"
    
    class Config:
        env_file = ".env"

settings = Settings()
