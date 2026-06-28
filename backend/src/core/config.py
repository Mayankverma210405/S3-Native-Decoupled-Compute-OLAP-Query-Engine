from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "S3 Native Decoupled Compute OLAP Query Engine"
    API_VERSION: str = "v1"

    DATABASE_URL: str

    AWS_REGION: str = "ap-south-1"

    LOG_LEVEL: str = "INFO"

    DEBUG: bool = False

    ENVIRONMENT: str = "development"
    
    S3_BUCKET_NAME: str = ""
        
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()