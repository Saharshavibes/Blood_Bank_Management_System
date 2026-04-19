from app.config import Settings


def test_cors_origins_accepts_comma_separated_values() -> None:
    settings = Settings(cors_origins="http://localhost:5173, https://example.org")

    assert settings.cors_origins == ["http://localhost:5173", "https://example.org"]


def test_cors_origins_accepts_json_array() -> None:
    settings = Settings(cors_origins='["http://localhost:5173", "https://example.org"]')

    assert settings.cors_origins == ["http://localhost:5173", "https://example.org"]
