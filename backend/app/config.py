from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "TRELLIS 3D Generator"
    API_VERSION: str = "v1"
    DEBUG: bool = False

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    STORAGE_PATH: str = "/app/storage"
    UPLOADS_PATH: str = "/app/storage/uploads"
    OUTPUTS_PATH: str = "/app/storage/outputs"
    PREVIEWS_PATH: str = "/app/storage/previews"

    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: List[str] = ["image/png", "image/jpeg", "image/webp"]

    TRELLIS_MODEL_PATH: str = "microsoft/TRELLIS-image-large"
    TRELLIS_TEXT_MODEL_PATH: str = "microsoft/TRELLIS-text-large"
    TRELLIS_DEVICE: str = "cuda"

    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.2"

    GROQ_API_KEY: Optional[str] = None
    GROQ_DEFAULT_MODEL: str = "llama-3.3-70b-versatile"

    JOB_TIMEOUT: int = 600
    JOB_RETENTION_HOURS: int = 24

    WORKER_COUNT: int = 1
    WORKER_QUEUE_NAME: str = "trellis_jobs"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
