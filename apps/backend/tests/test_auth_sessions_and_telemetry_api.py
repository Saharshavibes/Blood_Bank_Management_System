import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import auth as auth_api
from app.auth.dependencies import get_current_user, get_optional_current_user
from app.database.session import get_db
from app.main import app
from app.models.enums import DegradedState, DegradedStateSource, UserRole


class FakeScalarResult:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


class FakeSession:
    def __init__(self, scalar_values: list[object] | None = None) -> None:
        self.scalar_values = scalar_values or []
        self.added: list[object] = []
        self.refreshed: list[object] = []
        self.commit_calls = 0

    def add(self, value: object) -> None:
        self.added.append(value)

    def commit(self) -> None:
        self.commit_calls += 1

    def refresh(self, value: object) -> None:
        self.refreshed.append(value)
        if getattr(value, "id", None) is None:
            setattr(value, "id", uuid.uuid4())
        if getattr(value, "created_at", None) is None:
            setattr(value, "created_at", datetime.now(UTC))

    def scalars(self, *_args: object, **_kwargs: object) -> FakeScalarResult:
        return FakeScalarResult(self.scalar_values)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None, None, None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def override_db(session: FakeSession):
    def _override() -> Generator[FakeSession, None, None]:
        yield session

    return _override


def build_user(*, role: UserRole) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        email=f"{role.value}@example.com",
        role=role,
        donor_id=None,
        hospital_id=None,
        is_active=True,
    )


def build_token_payload(user: SimpleNamespace) -> dict[str, Any]:
    return {
        "access_token": "new-access-token",
        "token_type": "bearer",
        "expires_at": (datetime.now(UTC) + timedelta(minutes=30)).isoformat(),
        "refresh_token": "new-refresh-token",
        "refresh_expires_at": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "donor_id": None,
            "hospital_id": None,
            "is_active": True,
        },
    }


def test_refresh_rotates_active_refresh_token(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    user = build_user(role=UserRole.DONOR)
    refresh_record = SimpleNamespace(
        user=user,
        user_id=user.id,
        revoked_at=None,
        replaced_by_id=None,
        expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
    observed: dict[str, Any] = {}

    def fake_get_refresh_token_record(_db: object, token: str, *, lock: bool = False) -> object | None:
        observed["token"] = token
        observed["lock"] = lock
        return refresh_record

    def fake_build_token_response(
        _db: object,
        _user: object,
        *,
        rotate_from: object | None = None,
        issued_at: datetime | None = None,
    ) -> dict[str, Any]:
        observed["rotate_from"] = rotate_from
        observed["issued_at"] = issued_at
        return build_token_payload(user)

    monkeypatch.setattr(auth_api, "get_refresh_token_record", fake_get_refresh_token_record)
    monkeypatch.setattr(auth_api, "_build_token_response", fake_build_token_response)

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "x" * 32})

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["refresh_token"] == "new-refresh-token"
    assert observed["token"] == "x" * 32
    assert observed["lock"] is True
    assert observed["rotate_from"] is refresh_record
    assert isinstance(observed["issued_at"], datetime)
    assert session.commit_calls == 1


def test_refresh_detects_reuse_and_revokes_active_sessions(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    revoked_record = SimpleNamespace(
        user=None,
        user_id=uuid.uuid4(),
        revoked_at=datetime.now(UTC) - timedelta(minutes=1),
        replaced_by_id=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    observed: dict[str, Any] = {}

    def fake_get_refresh_token_record(_db: object, _token: str, *, lock: bool = False) -> object | None:
        observed["lock"] = lock
        return revoked_record

    def fake_revoke_active_user_refresh_tokens(
        _db: object,
        *,
        user_id: uuid.UUID,
        reason: str,
        revoked_at: datetime | None = None,
    ) -> int:
        observed["user_id"] = user_id
        observed["reason"] = reason
        observed["revoked_at"] = revoked_at
        return 1

    monkeypatch.setattr(auth_api, "get_refresh_token_record", fake_get_refresh_token_record)
    monkeypatch.setattr(auth_api, "revoke_active_user_refresh_tokens", fake_revoke_active_user_refresh_tokens)

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "y" * 32})

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token is invalid or expired"
    assert observed["lock"] is True
    assert observed["user_id"] == revoked_record.user_id
    assert observed["reason"] == "refresh_token_reuse_detected"
    assert isinstance(observed["revoked_at"], datetime)
    assert session.commit_calls == 1


def test_refresh_revokes_expired_refresh_token(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    user = build_user(role=UserRole.DONOR)
    expired_record = SimpleNamespace(
        user=user,
        user_id=user.id,
        revoked_at=None,
        replaced_by_id=None,
        expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )
    observed: dict[str, Any] = {}

    def fake_get_refresh_token_record(_db: object, _token: str, *, lock: bool = False) -> object | None:
        observed["lock"] = lock
        return expired_record

    def fake_revoke_refresh_token(
        refresh_token_record: object,
        *,
        reason: str,
        revoked_at: datetime | None = None,
    ) -> None:
        observed["record"] = refresh_token_record
        observed["reason"] = reason
        observed["revoked_at"] = revoked_at

    monkeypatch.setattr(auth_api, "get_refresh_token_record", fake_get_refresh_token_record)
    monkeypatch.setattr(auth_api, "revoke_refresh_token", fake_revoke_refresh_token)

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "z" * 32})

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token is invalid or expired"
    assert observed["lock"] is True
    assert observed["record"] is expired_record
    assert observed["reason"] == "expired"
    assert isinstance(observed["revoked_at"], datetime)
    assert session.commit_calls == 1


def test_refresh_revokes_when_user_inactive(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    inactive_user = build_user(role=UserRole.DONOR)
    inactive_user.is_active = False
    refresh_record = SimpleNamespace(
        user=inactive_user,
        user_id=inactive_user.id,
        revoked_at=None,
        replaced_by_id=None,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    observed: dict[str, Any] = {}

    def fake_get_refresh_token_record(_db: object, _token: str, *, lock: bool = False) -> object | None:
        observed["lock"] = lock
        return refresh_record

    def fake_revoke_refresh_token(
        refresh_token_record: object,
        *,
        reason: str,
        revoked_at: datetime | None = None,
    ) -> None:
        observed["record"] = refresh_token_record
        observed["reason"] = reason
        observed["revoked_at"] = revoked_at

    monkeypatch.setattr(auth_api, "get_refresh_token_record", fake_get_refresh_token_record)
    monkeypatch.setattr(auth_api, "revoke_refresh_token", fake_revoke_refresh_token)

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "w" * 32})

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token is invalid or expired"
    assert observed["lock"] is True
    assert observed["record"] is refresh_record
    assert observed["reason"] == "user_inactive"
    assert isinstance(observed["revoked_at"], datetime)
    assert session.commit_calls == 1


def test_logout_all_revokes_user_refresh_tokens(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    user = build_user(role=UserRole.ADMIN)
    app.dependency_overrides[get_current_user] = lambda: user

    observed: dict[str, Any] = {}

    def fake_revoke_active_user_refresh_tokens(_db: object, *, user_id: uuid.UUID, reason: str, revoked_at: datetime | None = None) -> int:
        observed["user_id"] = user_id
        observed["reason"] = reason
        observed["revoked_at"] = revoked_at
        return 2

    monkeypatch.setattr(auth_api, "revoke_active_user_refresh_tokens", fake_revoke_active_user_refresh_tokens)

    response = client.post("/api/v1/auth/logout-all")

    assert response.status_code == 200
    assert response.json()["message"] == "All sessions ended"
    assert observed["user_id"] == user.id
    assert observed["reason"] == "logout_all"
    assert session.commit_calls == 1


def test_create_degraded_event_attaches_authenticated_user(client: TestClient) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    user = build_user(role=UserRole.HOSPITAL)
    app.dependency_overrides[get_optional_current_user] = lambda: user

    response = client.post(
        "/api/v1/telemetry/degraded-state",
        json={
            "source": "inventory",
            "state": "degraded",
            "message": "inventory endpoint unavailable",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["source"] == "inventory"
    assert payload["state"] == "degraded"
    assert payload["user_id"] == str(user.id)
    assert session.commit_calls == 1
    assert len(session.added) == 1
    created_event = session.added[0]
    assert getattr(created_event, "user_id") == user.id


def test_list_degraded_events_requires_authentication(client: TestClient) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)

    response = client.get("/api/v1/telemetry/degraded-state")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_list_degraded_events_enforces_admin_role(client: TestClient) -> None:
    session = FakeSession()
    app.dependency_overrides[get_db] = override_db(session)
    app.dependency_overrides[get_current_user] = lambda: build_user(role=UserRole.DONOR)

    response = client.get("/api/v1/telemetry/degraded-state")

    assert response.status_code == 403
    assert "requires one of these roles: admin" in response.json()["detail"]


def test_list_degraded_events_returns_data_for_admin(client: TestClient) -> None:
    event_one = SimpleNamespace(
        id=uuid.uuid4(),
        source=DegradedStateSource.INVENTORY,
        state=DegradedState.DEGRADED,
        message="inventory degraded",
        user_id=uuid.uuid4(),
        created_at=datetime.now(UTC),
    )
    event_two = SimpleNamespace(
        id=uuid.uuid4(),
        source=DegradedStateSource.URGENT_ROUTING,
        state=DegradedState.RECOVERED,
        message="routing recovered",
        user_id=None,
        created_at=datetime.now(UTC),
    )

    session = FakeSession([event_one, event_two])
    app.dependency_overrides[get_db] = override_db(session)
    app.dependency_overrides[get_current_user] = lambda: build_user(role=UserRole.ADMIN)

    response = client.get("/api/v1/telemetry/degraded-state?limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["id"] == str(event_one.id)
    assert payload[0]["source"] == "inventory"
    assert payload[1]["id"] == str(event_two.id)
    assert payload[1]["state"] == "recovered"
