from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    gemini_api_key: str = ""
    jwt_secret: str = "flash-analytics-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    data_path: str = os.environ.get("DATA_PATH", "/app/Data")
    database_url: str = "postgresql://flash:flash123@localhost:5432/flash_analytics"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
