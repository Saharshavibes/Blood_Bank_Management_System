import json
from pathlib import Path
from typing import Annotated, Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = "postgresql+psycopg2://bbms_user:bbms_password@localhost:5432/blood_bank"
DEFAULT_JWT_SECRET_KEY = "change-this-secret-key"


class Settings(BaseSettings):
    app_name: str = "Blood Bank Management API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = DEFAULT_DATABASE_URL
    jwt_secret_key: str = DEFAULT_JWT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 14
    refresh_token_entropy_bytes: int = 48
    admin_bootstrap_token: str = ""
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("DATABASE_URL must be a string")

        normalized = value.strip()
        if not normalized:
            raise ValueError("DATABASE_URL must not be empty")

        if normalized.startswith("postgres://"):
            return f"postgresql+psycopg2://{normalized[len('postgres://') :]}"

        if normalized.startswith("postgresql://"):
            return f"postgresql+psycopg2://{normalized[len('postgresql://') :]}"

        return normalized

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

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("JWT_SECRET_KEY must not be empty")
        return normalized

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment.lower() != "production":
            return self

        if self.database_url == DEFAULT_DATABASE_URL:
            raise ValueError("DATABASE_URL must be explicitly configured in production")

        if self.jwt_secret_key == DEFAULT_JWT_SECRET_KEY or len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters and not use the default value in production")

        if not self.cors_origins:
            raise ValueError("CORS_ORIGINS must not be empty in production")

        if any("*" in origin for origin in self.cors_origins):
            raise ValueError("CORS_ORIGINS wildcard values are not allowed in production")

        return self

    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
