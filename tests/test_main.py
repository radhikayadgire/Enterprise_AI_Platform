"""Happy-path tests for the Enterprise AI Platform API routes."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_happy_path():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_happy_path():
    response = client.post("/api/search", json={"query": "quarterly report"})
    assert response.status_code == 200
    assert "quarterly report" in response.json()["result"]


def test_email_happy_path():
    payload = {"to": "alice@example.com", "subject": "Hello", "body": "Hi there"}
    response = client.post("/api/email", json=payload)
    assert response.status_code == 200
    assert response.json() == {"to": "alice@example.com", "subject": "Hello", "status": "sent"}


def test_hr_happy_path():
    response = client.post("/api/hr", json={"question": "How many leave days do I get?"})
    assert response.status_code == 200
    assert "leave" in response.json()["answer"].lower()


def test_coordinator_happy_path():
    response = client.post("/api/coordinator", json={"query": "What is my insurance coverage?"})
    assert response.status_code == 200
    assert "insurance" in response.json()["result"].lower()
