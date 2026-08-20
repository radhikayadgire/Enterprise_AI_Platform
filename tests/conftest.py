"""
Pytest fixtures and configuration for Streamlit UI automation tests.
"""
import os
import subprocess
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def streamlit_app():
    """Start the Streamlit app for testing and tear down after tests."""
    # Get the path to the UI app
    ui_dir = Path(__file__).parent.parent / "ui"
    app_path = ui_dir / "app.py"

    # Start Streamlit in a subprocess
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_SERVER_PORT"] = "8501"

    process = subprocess.Popen(
        ["streamlit", "run", str(app_path), "--server.port", "8501"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for the app to start
    time.sleep(3)

    yield "http://localhost:8501"

    # Teardown: kill the process
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="function")
def browser_context(streamlit_app):
    """Create a new browser context for each test."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(streamlit_app)
        # Wait for Streamlit to be ready
        page.wait_for_selector("text=Enterprise AI Platform", timeout=10000)
        yield page
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def clean_user_details_file():
    """Remove the user_details.csv file before each test."""
    data_dir = Path(__file__).parent.parent / "data"
    user_details_file = data_dir / "user_details.csv"

    if user_details_file.exists():
        user_details_file.unlink()

    yield

    # Cleanup after test
    if user_details_file.exists():
        user_details_file.unlink()
