# Automation Tests

This directory contains automated tests for the Enterprise AI Platform Streamlit application.

## Framework

- **Test Framework**: pytest
- **UI Testing**: Streamlit AppTest (streamlit.testing.v1)
- **Language**: Python 3.x

## Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_user_details.py
```

Run specific test class:
```bash
pytest tests/test_user_details.py::TestUserDetailsHappyPath
```

Run specific test:
```bash
pytest tests/test_user_details.py::TestUserDetailsHappyPath::test_submit_valid_user_details
```

Run with verbose output:
```bash
pytest -v
```

## Test Coverage

### test_user_details.py

Tests for the User Details feature (MT-5) - a form where users can enter their name and phone number.

#### Test Classes

1. **TestUserDetailsHappyPath**: Tests for successful user details submission
   - `test_submit_valid_user_details`: Verify form submission with valid data
   - `test_submitted_details_displayed_in_table`: Verify submitted details appear in the table

2. **TestUserDetailsValidation**: Tests for form validation
   - `test_reject_empty_name`: Verify error when name field is empty
   - `test_reject_invalid_phone_number`: Verify error when phone contains invalid characters
   - `test_reject_empty_phone_number`: Verify error when phone field is empty
   - `test_reject_phone_number_too_short`: Verify error when phone is less than 7 digits
   - `test_reject_phone_number_too_long`: Verify error when phone is more than 15 characters

3. **TestUserDetailsEdgeCases**: Tests for boundary conditions
   - `test_phone_number_minimum_length`: Verify acceptance of exactly 7 digits
   - `test_phone_number_maximum_length`: Verify acceptance of exactly 15 characters
   - `test_phone_number_with_spaces_and_hyphens`: Verify acceptance of formatted phone numbers
   - `test_phone_number_with_leading_plus`: Verify acceptance of international format

4. **TestUserDetailsE2E**: End-to-end workflow tests
   - `test_navigate_from_home_to_user_details`: Verify navigation from Home page
   - `test_navigate_from_contact_us_to_user_details`: Verify navigation from Contact Us page

5. **TestUserDetailsDataPersistence**: Tests for CSV data storage
   - `test_data_persisted_to_csv`: Verify data is saved to CSV file
   - `test_multiple_submissions_append_to_csv`: Verify multiple submissions append correctly

## Test Isolation

Tests are automatically isolated using the `isolate_data_dir` fixture in `conftest.py`. Each test runs with a temporary data directory, preventing:
- Tests from interfering with each other
- Tests from modifying production data
- Flaky tests due to shared state

## Notes

- Tests use index-based widget access (e.g., `app.text_input[0]`) since the UI doesn't set explicit widget keys
- The test suite does not require the app to be running - AppTest launches it programmatically
- All tests are designed to be deterministic and repeatable
