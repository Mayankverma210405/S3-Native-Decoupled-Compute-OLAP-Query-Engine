from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "S3 Native Decoupled Compute OLAP Query Engine"
    API_VERSION: str = "v1"
    
    DATABASE_URL: str

    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "storage"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()