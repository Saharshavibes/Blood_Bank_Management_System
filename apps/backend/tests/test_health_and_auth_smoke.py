from fastapi.testclient import TestClient

from app.api.v1 import health as health_api
from app.database.session import get_db
from app.main import app


class _HealthCheckResult:
    def __init__(self, rows: list[tuple[str]]) -> None:
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)


class _HealthCheckSession:
    def execute(self, statement: object, *_args: object, **_kwargs: object) -> _HealthCheckResult:
        if "alembic_version" in str(statement):
            return _HealthCheckResult([("test-migration-head",)])
        return _HealthCheckResult([])

    def close(self) -> None:
        return None


def _override_health_db():
    db = _HealthCheckSession()
    try:
        yield db
    finally:
        db.close()


def test_health_endpoint_returns_ok() -> None:
    app.dependency_overrides[get_db] = _override_health_db
    client = TestClient(app)

    try:
        response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_auth_me_requires_bearer_token() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_migration_state_endpoint_returns_aligned_payload(monkeypatch) -> None:
    app.dependency_overrides[get_db] = _override_health_db
    monkeypatch.setattr(health_api, "_expected_migration_heads", lambda: {"test-migration-head"})
    client = TestClient(app)

    try:
        response = client.get("/api/v1/health/migration-state")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["migration_state"]["aligned"] is True
    assert payload["migration_state"]["expected_heads"] == ["test-migration-head"]
    assert payload["migration_state"]["current_versions"] == ["test-migration-head"]
