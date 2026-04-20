from app.config import Settings


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
