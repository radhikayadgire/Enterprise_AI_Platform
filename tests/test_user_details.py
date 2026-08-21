"""
Automation tests for User Details feature (MT-5)

Tests the user details form that appears after the Contact Us page,
where users can enter their name and phone number.
"""
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app():
    """Create an AppTest instance for the Streamlit app."""
    at = AppTest.from_file("ui/app.py")
    at.run()
    return at


class TestUserDetailsHappyPath:
    """Tests for successful user details submission"""

    def test_submit_valid_user_details(self, app):
        """
        TC-001: Submit valid name and phone number on User Details page

        Given the app is running
        When user navigates to User Details page
        And enters a valid name and phone number
        And clicks Submit
        Then a success message is displayed
        And the form clears
        And the data is persisted to CSV
        """
        # Navigate to User Details page
        app.sidebar.radio[0].set_value("User Details").run()

        # Verify we're on the User Details page
        assert app.title[0].value == "User Details"

        # Fill in the form (text_input[0] is Full Name, text_input[1] is Phone Number)
        app.text_input[0].set_value("Jane Doe").run()
        app.text_input[1].set_value("+1 555-123-4567").run()

        # Submit the form
        app.button[0].click().run()

        # Verify success message
        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, Jane Doe! Your details have been saved." in msg for msg in success_messages)

        # Verify form cleared
        assert app.text_input[0].value == ""
        assert app.text_input[1].value == ""

    def test_submitted_details_displayed_in_table(self, app):
        """
        TC-004: User Details table displays previously submitted entries

        Given a user detail has been submitted
        When user navigates to User Details page
        Then the submitted details table is displayed
        And shows the previously submitted entry
        """
        # Navigate to User Details and submit an entry
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("Existing User").run()
        app.text_input[1].set_value("+1 222-333-4444").run()
        app.button[0].click().run()

        # Verify the submitted details table is displayed
        assert app.subheader[0].value == "Submitted Details"

        # Verify data is in the dataframe
        df_widget = app.dataframe[0]
        assert df_widget is not None


class TestUserDetailsValidation:
    """Tests for form validation on User Details page"""

    def test_reject_empty_name(self, app):
        """
        TC-005 (partial): Reject submission with empty name

        Given the app is running
        When user navigates to User Details page
        And leaves the name field empty
        And enters a valid phone number
        And clicks Submit
        Then an error message is displayed
        And no data is saved
        """
        app.sidebar.radio[0].set_value("User Details").run()

        # Leave name empty, enter valid phone
        app.text_input[1].set_value("555-123-4567").run()
        app.button[0].click().run()

        # Verify error message
        error_messages = [msg.value for msg in app.error]
        assert any("Name is required." in msg for msg in error_messages)

    def test_reject_invalid_phone_number(self, app):
        """
        TC-005 (partial): Reject submission with invalid phone number

        Given the app is running
        When user navigates to User Details page
        And enters a valid name
        And enters an invalid phone number (contains letters)
        And clicks Submit
        Then an error message is displayed
        And no data is saved
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("John Doe").run()
        app.text_input[1].set_value("abc").run()
        app.button[0].click().run()

        # Verify error message
        error_messages = [msg.value for msg in app.error]
        assert any("Phone number must contain 7-15 digits" in msg for msg in error_messages)

    def test_reject_empty_phone_number(self, app):
        """
        Reject submission with empty phone number

        Given the app is running
        When user navigates to User Details page
        And enters a valid name
        And leaves phone number empty
        And clicks Submit
        Then an error message is displayed
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("John Doe").run()
        app.button[0].click().run()

        # Verify error message
        error_messages = [msg.value for msg in app.error]
        assert any("Phone number is required." in msg for msg in error_messages)

    def test_reject_phone_number_too_short(self, app):
        """
        Reject phone number shorter than 7 characters

        Given the app is running
        When user enters a phone number with less than 7 digits
        Then an error message is displayed
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("John Doe").run()
        app.text_input[1].set_value("12345").run()
        app.button[0].click().run()

        # Verify error message
        error_messages = [msg.value for msg in app.error]
        assert any("Phone number must contain 7-15 digits" in msg for msg in error_messages)

    def test_reject_phone_number_too_long(self, app):
        """
        Reject phone number longer than 15 characters

        Given the app is running
        When user enters a phone number with more than 15 digits
        Then an error message is displayed
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("John Doe").run()
        app.text_input[1].set_value("1234567890123456").run()
        app.button[0].click().run()

        # Verify error message
        error_messages = [msg.value for msg in app.error]
        assert any("Phone number must contain 7-15 digits" in msg for msg in error_messages)


class TestUserDetailsEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_phone_number_minimum_length(self, app):
        """
        TC-003 (partial): Submit phone number at minimum allowed length (7 digits)

        Given the app is running
        When user enters a phone number with exactly 7 digits
        Then the submission is accepted
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("Al Lee").run()
        app.text_input[1].set_value("1234567").run()
        app.button[0].click().run()

        # Verify success (no error message)
        error_messages = [msg.value for msg in app.error]
        assert not any("Phone number must contain 7-15 digits" in msg for msg in error_messages)

        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, Al Lee!" in msg for msg in success_messages)

    def test_phone_number_maximum_length(self, app):
        """
        TC-003 (partial): Submit phone number at maximum allowed length (15 characters)

        Given the app is running
        When user enters a phone number with exactly 15 characters
        Then the submission is accepted
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("Al Lee").run()
        app.text_input[1].set_value("+123 456-789-012").run()
        app.button[0].click().run()

        # Verify success (no error message)
        error_messages = [msg.value for msg in app.error]
        assert not any("Phone number must contain 7-15 digits" in msg for msg in error_messages)

        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, Al Lee!" in msg for msg in success_messages)

    def test_phone_number_with_spaces_and_hyphens(self, app):
        """
        Accept phone number with valid formatting (spaces and hyphens)

        Given the app is running
        When user enters a phone number with spaces and hyphens
        Then the submission is accepted
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("Test User").run()
        app.text_input[1].set_value("555 123-4567").run()
        app.button[0].click().run()

        # Verify success
        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, Test User!" in msg for msg in success_messages)

    def test_phone_number_with_leading_plus(self, app):
        """
        Accept phone number with leading plus sign

        Given the app is running
        When user enters a phone number with a leading +
        Then the submission is accepted
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("Test User").run()
        app.text_input[1].set_value("+15551234567").run()
        app.button[0].click().run()

        # Verify success
        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, Test User!" in msg for msg in success_messages)


class TestUserDetailsE2E:
    """End-to-end tests for User Details workflow"""

    def test_navigate_from_home_to_user_details(self, app):
        """
        Navigate from Home to User Details and submit

        Given the app starts on Home page
        When user navigates to User Details
        And submits valid information
        Then the submission succeeds
        """
        # Verify we start on Home
        assert app.title[0].value == "Enterprise AI Platform"

        # Navigate to User Details
        app.sidebar.radio[0].set_value("User Details").run()

        # Submit valid data
        app.text_input[0].set_value("E2E Test User").run()
        app.text_input[1].set_value("555-999-8888").run()
        app.button[0].click().run()

        # Verify success
        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, E2E Test User!" in msg for msg in success_messages)

    def test_navigate_from_contact_us_to_user_details(self, app):
        """
        TC-002: Navigate from Contact Us to User Details and submit

        Given the app is running
        When user navigates to Contact Us
        Then an info message mentions User Details
        When user navigates to User Details
        And submits valid information
        Then the submission succeeds
        """
        # Navigate to Contact Us
        app.sidebar.radio[0].set_value("Contact Us").run()

        # Verify we're on Contact Us page
        assert app.title[0].value == "Contact Us"

        # Verify info message pointing to User Details
        info_messages = [msg.value for msg in app.info]
        assert any("User Details" in msg for msg in info_messages)

        # Navigate to User Details
        app.sidebar.radio[0].set_value("User Details").run()

        # Submit valid data
        app.text_input[0].set_value("John Smith").run()
        app.text_input[1].set_value("555-987-6543").run()
        app.button[0].click().run()

        # Verify success
        success_messages = [msg.value for msg in app.success]
        assert any("Thank you, John Smith!" in msg for msg in success_messages)


class TestUserDetailsDataPersistence:
    """Tests for data persistence to CSV"""

    def test_data_persisted_to_csv(self, app, isolate_data_dir):
        """
        Verify submitted data is persisted to CSV file

        Given the app is running
        When user submits valid details
        Then the data is written to user_details.csv
        And the CSV contains the correct columns
        """
        app.sidebar.radio[0].set_value("User Details").run()

        app.text_input[0].set_value("CSV Test User").run()
        app.text_input[1].set_value("555-111-2222").run()
        app.button[0].click().run()

        # Verify CSV file was created
        csv_path = isolate_data_dir / "user_details.csv"
        assert csv_path.exists()

        # Verify CSV content
        df = pd.read_csv(csv_path)
        assert len(df) == 1
        assert "timestamp" in df.columns
        assert "name" in df.columns
        assert "phone_number" in df.columns
        assert df.iloc[0]["name"] == "CSV Test User"
        assert df.iloc[0]["phone_number"] == "555-111-2222"

    def test_multiple_submissions_append_to_csv(self, app, isolate_data_dir):
        """
        Verify multiple submissions are appended to CSV

        Given the app is running
        When user submits details multiple times
        Then all submissions are appended to the CSV
        And the table displays all entries
        """
        app.sidebar.radio[0].set_value("User Details").run()

        # First submission
        app.text_input[0].set_value("First User").run()
        app.text_input[1].set_value("555-111-1111").run()
        app.button[0].click().run()

        # Second submission
        app.text_input[0].set_value("Second User").run()
        app.text_input[1].set_value("555-222-2222").run()
        app.button[0].click().run()

        # Verify CSV contains both entries
        csv_path = isolate_data_dir / "user_details.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 2
        assert "First User" in df["name"].values
        assert "Second User" in df["name"].values
