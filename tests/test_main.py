"""Tests for the backend API routes.

Covers both happy-path scenarios and error handling added in the PR.

Run with: pytest
"""

from unittest.mock import patch

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


def test_get_contact_info_when_none_returns_404():
    """GET /contact should return 404 when CONTACT_INFO is None."""
    with patch("backend.main.CONTACT_INFO", None):
        response = client.get("/contact")

        assert response.status_code == 404
        assert response.json() == {"detail": "Contact information not found"}


def test_nonexistent_route_returns_404():
    """Requesting a nonexistent route should return 404 with structured error."""
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_unsupported_method_returns_405():
    """Requesting an existing route with unsupported method should return 405."""
    response = client.post("/contact")

    assert response.status_code == 405
    assert "detail" in response.json()


def test_unhandled_exception_returns_500():
    """Unexpected exceptions should be caught by the global handler and return 500."""
    # Simulate an unexpected exception by patching the root handler to raise
    def mock_read_root():
        raise RuntimeError("Simulated unexpected error")

    with patch("backend.main.read_root", mock_read_root):
        response = client.get("/")

        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}
