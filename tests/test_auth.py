"""Tests for the login/registration API added to backend/main.py."""
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from backend import database, main
from backend.database import Base, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


main.app.dependency_overrides[get_db] = override_get_db
client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_register_new_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "supersecret"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert "hashed_password" not in body


def test_register_duplicate_username_rejected():
    client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "other@example.com", "password": "supersecret"},
    )
    assert response.status_code == 400


def test_login_success_returns_token():
    client.post(
        "/api/auth/register",
        json={"username": "carol", "email": "carol@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "carol", "password": "supersecret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_rejected():
    client.post(
        "/api/auth/register",
        json={"username": "dave", "email": "dave@example.com", "password": "supersecret"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "dave", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_requires_valid_token():
    client.post(
        "/api/auth/register",
        json={"username": "erin", "email": "erin@example.com", "password": "supersecret"},
    )
    token = client.post(
        "/api/auth/login",
        data={"username": "erin", "password": "supersecret"},
    ).json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "erin"

    unauthorized = client.get("/api/auth/me")
    assert unauthorized.status_code == 401
