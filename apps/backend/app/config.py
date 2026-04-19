import json
from pathlib import Path
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "Blood Bank Management API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "postgresql+psycopg2://bbms_user:bbms_password@localhost:5432/blood_bank"
    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 14
    refresh_token_entropy_bytes: int = 48
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return []
            if normalized.startswith("["):
                parsed = json.loads(normalized)
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON value must be a list")
                return [origin.strip() for origin in parsed if isinstance(origin, str) and origin.strip()]
            return [origin.strip() for origin in normalized.split(",") if origin.strip()]
        if isinstance(value, list):
            return [origin.strip() for origin in value if isinstance(origin, str) and origin.strip()]
        raise ValueError("CORS_ORIGINS must be a list or a comma-separated string")

    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
