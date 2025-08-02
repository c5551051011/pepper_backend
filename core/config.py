# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # SMS Service (for phone verification)
    SMS_API_KEY: Optional[str] = os.getenv("SMS_API_KEY")
    SMS_SENDER: str = "StoreCredit"

    # App Settings
    APP_NAME: str = "StoreCredit Pro"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Performance
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30

    class Config:
        env_file = ".env"


settings = Settings()