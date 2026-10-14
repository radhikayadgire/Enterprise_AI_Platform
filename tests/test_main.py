from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _login() -> dict:
    resp = client.post("/auth/login", data={"username": "jdoe", "password": "password123"})
    assert resp.status_code == 200
    return resp.json()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_login_success():
    body = _login()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 60


def test_login_failure():
    resp = client.post("/auth/login", data={"username": "jdoe", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_valid_token():
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token():
    tokens = _login()
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "jdoe"


def test_refresh_endpoint():
    tokens = _login()
    resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert resp.json()["access_token"] != tokens["access_token"]


def test_chat_routes_to_hr_agent():
    tokens = _login()
    resp = client.post(
        "/chat",
        json={"message": "What is the leave policy?"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    assert resp.json()["agent"] == "hr_agent"


def test_chat_requires_auth():
    resp = client.post("/chat", json={"message": "hello"})
    assert resp.status_code == 401
