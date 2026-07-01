from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = ""

    # JWT
    jwt_secret: str = "change-this-to-a-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Database
    database_url: str = "postgresql://flash:flash123@localhost:5432/flash_analytics"

    # Data
    data_path: str = "/app/data"

    # Users (JSON string)
    default_users: str = '{"admin@flash.com":{"password":"flash123","name":"Admin Flash","role":"admin"}}'

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
