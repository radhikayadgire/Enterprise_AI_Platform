"""
Pytest configuration and shared fixtures for test suite
"""
import pytest


@pytest.fixture(autouse=True)
def isolate_data_dir(monkeypatch, tmp_path):
    """
    Isolate each test by redirecting the data directory to a temporary location.
    This prevents tests from interfering with each other and with production data.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)

    # Patch the DATA_DIR constant in ui.app module
    monkeypatch.setattr("ui.app.DATA_DIR", str(data_dir))
    monkeypatch.setattr("ui.app.USER_DETAILS_CSV", str(data_dir / "user_details.csv"))

    return data_dir
