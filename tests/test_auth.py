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


def test_register_creates_new_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    user = response.json()
    assert user["username"] == "bob"
    assert user["email"] == "bob@example.com"
    assert "id" in user
    assert "password" not in user
    assert "hashed_password" not in user


def test_register_rejects_duplicate_username():
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "different@example.com", "password": "hunter22"},
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_register_rejects_duplicate_email():
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/register",
        json={"username": "different", "email": "alice@example.com", "password": "hunter22"},
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_with_mobile_device_header():
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "hunter22"},
        headers={"X-Device-Type": "mobile"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"


def test_login_with_web_device_header():
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "hunter22"},
        headers={"X-Device-Type": "web"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]


def test_login_defaults_to_web_when_device_header_missing():
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "hunter22"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert tokens["access_token"]


def test_login_rejects_incorrect_password():
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "wrong-password"},
        headers={"X-Device-Type": "mobile"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_rejects_nonexistent_user():
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent", "password": "hunter22"},
        headers={"X-Device-Type": "mobile"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_complete_session_lifecycle():
    """E2E test: register → login → access protected → refresh → access again → logout."""
    # Register
    register_response = client.post(
        "/api/auth/register",
        json={"username": "charlie", "email": "charlie@example.com", "password": "pass1234"},
    )
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/api/auth/login",
        data={"username": "charlie", "password": "pass1234"},
        headers={"X-Device-Type": "mobile"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token_1 = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Access protected endpoint with first access token
    me_response_1 = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token_1}"},
    )
    assert me_response_1.status_code == 200
    assert me_response_1.json()["username"] == "charlie"

    # Refresh to get new access token
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    access_token_2 = refresh_response.json()["access_token"]
    assert access_token_2 != access_token_1

    # Access protected endpoint with new access token
    me_response_2 = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token_2}"},
    )
    assert me_response_2.status_code == 200
    assert me_response_2.json()["username"] == "charlie"

    # Logout
    logout_response = client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 204

    # Verify refresh token no longer works
    refresh_after_logout = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_after_logout.status_code == 401


def test_multiple_devices_can_have_independent_sessions():
    """Test that same user can log in from mobile and web independently."""
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "hunter22"},
    )

    # Login from mobile
    mobile_login = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "hunter22"},
        headers={"X-Device-Type": "mobile"},
    )
    assert mobile_login.status_code == 200
    mobile_tokens = mobile_login.json()

    # Login from web
    web_login = client.post(
        "/api/auth/login",
        data={"username": "alice", "password": "hunter22"},
        headers={"X-Device-Type": "web"},
    )
    assert web_login.status_code == 200
    web_tokens = web_login.json()

    # Both sessions should have different refresh tokens
    assert mobile_tokens["refresh_token"] != web_tokens["refresh_token"]

    # Both access tokens should work
    mobile_me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {mobile_tokens['access_token']}"},
    )
    assert mobile_me.status_code == 200

    web_me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {web_tokens['access_token']}"},
    )
    assert web_me.status_code == 200

    # Logout mobile session shouldn't affect web session
    client.post("/api/auth/logout", json={"refresh_token": mobile_tokens["refresh_token"]})

    mobile_refresh = client.post(
        "/api/auth/refresh",
        json={"refresh_token": mobile_tokens["refresh_token"]},
    )
    assert mobile_refresh.status_code == 401

    web_refresh = client.post(
        "/api/auth/refresh",
        json={"refresh_token": web_tokens["refresh_token"]},
    )
    assert web_refresh.status_code == 200


def test_access_token_cannot_be_used_for_refresh():
    """Verify token type validation: access tokens can't be used in refresh endpoint."""
    tokens = _register_and_login()
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert response.status_code == 401
    assert "Invalid or expired refresh token" in response.json()["detail"]


def test_refresh_token_cannot_be_used_for_protected_endpoints():
    """Verify token type validation: refresh tokens can't be used for /me."""
    tokens = _register_and_login()
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_health_check_endpoint():
    """Verify the health check endpoint is accessible without auth."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
