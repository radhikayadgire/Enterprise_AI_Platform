# Automation Tests for Enterprise AI Platform

This directory contains automated browser tests for the Streamlit-based Enterprise AI Platform application.

## Test Framework

- **Test Runner**: pytest
- **Browser Automation**: Playwright
- **Language**: Python 3.x

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

3. Start the Streamlit application (in a separate terminal):
   ```bash
   streamlit run ui/app.py
   ```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test markers
```bash
# Run only happy path tests
pytest tests/ -m happy_path

# Run only negative tests
pytest tests/ -m negative

# Run only edge case tests
pytest tests/ -m edge_case

# Run only E2E tests
pytest tests/ -m e2e
```

### Run a specific test file
```bash
pytest tests/test_user_details.py
```

### Run a specific test
```bash
pytest tests/test_user_details.py::TestUserDetailsForm::test_submit_valid_user_details
```

## Test Configuration

- **pytest.ini**: Contains pytest configuration and custom markers
- **conftest.py**: Contains shared fixtures for browser setup and page management
- **Default URL**: http://localhost:8501 (can be overridden via STREAMLIT_URL environment variable)

### Environment Variables

- `STREAMLIT_URL`: Override the default Streamlit app URL
  ```bash
  STREAMLIT_URL=http://localhost:8502 pytest tests/
  ```

## Test Coverage

The test suite covers the User Details form functionality:

### Happy Path Tests
- Submit valid user details with standard phone number
- Submit with international phone format (+ prefix)
- Submit multiple users sequentially

### Edge Cases
- Phone number at minimum length boundary (7 digits)
- Phone number exceeding maximum length (16 digits)

### Negative Tests
- Submit with empty name field
- Submit with non-numeric phone number

### E2E Tests
- Complete navigation flow: Home → Contact Us → User Details → Submit

## Test Markers

Available pytest markers:
- `@pytest.mark.happy_path` - Happy path scenarios
- `@pytest.mark.edge_case` - Edge case scenarios
- `@pytest.mark.negative` - Negative test scenarios
- `@pytest.mark.e2e` - End-to-end test scenarios

## CI/CD Integration

To run tests in headless mode (already configured by default):
```bash
pytest tests/
```

The browser is configured to run in headless mode by default in `conftest.py`.
