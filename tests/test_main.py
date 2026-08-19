"""Happy-path tests for the backend API routes.

Run with: pytest
"""

from fastapi.testclient import TestClient

from backend.main import CONTACT_INFO, app

client = TestClient(app)


def test_read_root_happy_path():
    """GET / should report the service is up and running."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Enterprise AI Platform API"}


def test_get_contact_info_happy_path():
    """GET /contact should return the configured contact details."""
    response = client.get("/contact")

    assert response.status_code == 200
    assert response.json() == {
        "name": CONTACT_INFO.name,
        "phone": CONTACT_INFO.phone,
        "email": CONTACT_INFO.email,
    }
