# Automation Tests

This directory contains automated UI tests for the Enterprise AI Platform Streamlit application.

## Setup

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Running Tests

Run all tests:
```bash
cd tests
pytest
```

Run specific test file:
```bash
pytest test_user_details_page.py
```

Run tests with specific markers:
```bash
pytest -m smoke
```

Run tests in parallel:
```bash
pytest -n auto
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_user_details_page.py` - Tests for User Details form functionality

## Test Coverage

The test suite covers:
- Navigation: User Details page placement after Contact Us
- Form validation: Empty fields, invalid phone format
- Successful submission: Valid data, whitespace handling
- Data persistence: CSV file creation and content verification
- End-to-end flows: Complete user journey from Home through submission

## Notes

- Tests automatically start and stop the Streamlit app
- Each test runs with a clean slate (CSV file cleanup)
- Tests run in headless Chrome by default
- Default Streamlit port: 8501
