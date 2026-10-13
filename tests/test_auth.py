"""Tests for the login/refresh/logout session flow (IMS-4)."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./backend/test_app.db")
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

import pytest
from fastapi.testclient import TestClient

from backend.database import Base, SessionLocal, engine
from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    SessionLocal().close()


def _register_and_login(device: str = "mobile"):
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "hunter22"},
        headers={"X-Device-Type": device},
    )
    assert response.status_code == 200
    return response.json()


def test_login_issues_access_and_refresh_tokens():
    tokens = _register_and_login()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    # 30 minutes, not 10 seconds.
    assert tokens["expires_in"] == 30 * 60


def test_access_token_authorizes_protected_endpoint():
    tokens = _register_and_login()
    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_refresh_token_mints_new_access_token_without_relogin():
    tokens = _register_and_login()
    response = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    new_access_token = response.json()["access_token"]
    assert new_access_token

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_logout_revokes_refresh_token():
    tokens = _register_and_login()
    logout_response = client.post("/api/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_response.status_code == 204

    refresh_response = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 401


def test_invalid_refresh_token_is_rejected():
    response = client.post("/api/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 401


def test_invalid_access_token_is_rejected():
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
