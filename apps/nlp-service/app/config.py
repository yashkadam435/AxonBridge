from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    REDIS_URL: str = "redis://axonbridge-redis:6379/1"
    GPU_MEMORY_LIMIT_GB: int = 16
    MODELS_DIR: str = "/app/models"
    
    # Fallback to Cloud APIs if local models are stubbed
    USE_CLOUD_FALLBACKS: bool = True
    GOOGLE_CLOUD_PROJECT: str = ""
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
