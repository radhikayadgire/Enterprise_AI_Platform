"""Happy-path tests for the API routes in backend/main.py."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_hr_query_happy_path():
    response = client.post("/api/hr/query", json={"question": "How much leave do I accrue?"})
    assert response.status_code == 200
    assert "leave" in response.json()["answer"].lower()


def test_search_happy_path():
    response = client.post("/api/search", json={"query": "leave"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert any(doc["id"] == "leave-policy" for doc in results)


def test_email_send_happy_path():
    response = client.post(
        "/api/email/send",
        json={"to": "employee@example.com", "subject": "Hello", "body": "Hi there"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "to": "employee@example.com",
        "subject": "Hello",
        "status": "sent",
    }


def test_coordinator_chat_happy_path():
    response = client.post(
        "/api/coordinator/chat", json={"message": "What is the insurance policy?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == "hr_agent"
    assert "insurance" in body["response"].lower()


def test_submit_user_details_happy_path():
    response = client.post(
        "/api/user",
        json={"name": "Jamie Rivera", "email": "jamie@example.com", "phone": "555-1234"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "received", "name": "Jamie Rivera"}
