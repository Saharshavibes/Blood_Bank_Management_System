import pytest

from app.config import DEFAULT_DATABASE_URL, Settings


def test_cors_origins_accepts_comma_separated_values() -> None:
    settings = Settings(cors_origins="http://localhost:5173, https://example.org")

    assert settings.cors_origins == ["http://localhost:5173", "https://example.org"]


def test_cors_origins_accepts_json_array() -> None:
    settings = Settings(cors_origins='["http://localhost:5173", "https://example.org"]')

    assert settings.cors_origins == ["http://localhost:5173", "https://example.org"]


def test_database_url_normalizes_postgres_scheme() -> None:
    settings = Settings(database_url="postgres://bbms_user:bbms_password@localhost:5432/blood_bank")

    assert settings.database_url == "postgresql+psycopg2://bbms_user:bbms_password@localhost:5432/blood_bank"


def test_database_url_normalizes_postgresql_scheme_without_driver() -> None:
    settings = Settings(database_url="postgresql://bbms_user:bbms_password@localhost:5432/blood_bank")

    assert settings.database_url == "postgresql+psycopg2://bbms_user:bbms_password@localhost:5432/blood_bank"


def test_production_rejects_default_database_url() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL must be explicitly configured in production"):
        Settings(
            environment="production",
            database_url=DEFAULT_DATABASE_URL,
            jwt_secret_key="a" * 32,
            cors_origins="https://frontend.example.com",
        )


def test_production_rejects_weak_jwt_secret() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET_KEY must be at least 32 characters"):
        Settings(
            environment="production",
            database_url="postgresql+psycopg2://service_user:service_password@db.example.com:5432/blood_bank",
            jwt_secret_key="weak-secret",
            cors_origins="https://frontend.example.com",
        )


def test_production_rejects_wildcard_cors_origin() -> None:
    with pytest.raises(ValueError, match="CORS_ORIGINS wildcard values are not allowed in production"):
        Settings(
            environment="production",
            database_url="postgresql+psycopg2://service_user:service_password@db.example.com:5432/blood_bank",
            jwt_secret_key="a" * 32,
            cors_origins="https://*.example.com",
        )


def test_production_accepts_explicit_secure_settings() -> None:
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg2://service_user:service_password@db.example.com:5432/blood_bank",
        jwt_secret_key="a" * 32,
        cors_origins="https://frontend.example.com",
    )

    assert settings.environment == "production"
    assert settings.cors_origins == ["https://frontend.example.com"]
