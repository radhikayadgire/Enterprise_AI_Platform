"""Pytest configuration and shared fixtures for Streamlit app automation tests."""
import os
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the Streamlit app."""
    return os.getenv("STREAMLIT_URL", "http://localhost:8501")


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Create and yield a Playwright instance for the test session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    """Launch a browser instance for the test session."""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, base_url: str) -> Generator[Page, None, None]:
    """Create a new page and navigate to the app for each test."""
    page = context.new_page()
    page.goto(base_url)
    # Wait for Streamlit to initialize
    page.wait_for_load_state("networkidle")
    yield page
    page.close()
