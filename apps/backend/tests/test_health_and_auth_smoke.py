from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "environment" in payload


def test_auth_me_requires_bearer_token() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
