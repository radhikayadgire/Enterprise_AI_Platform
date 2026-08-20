"""
Tests for the User Details page functionality.

Tests cover the new User Details form introduced in MT-5:
- Navigation placement (after Contact Us)
- Form validation (name, phone)
- Successful submission
- Data persistence to CSV
"""
import csv
from pathlib import Path

import pytest


class TestUserDetailsNavigation:
    """Test User Details page navigation and placement."""

    def test_user_details_appears_after_contact_us_in_sidebar(self, browser_context):
        """Verify User Details option appears immediately after Contact Us in navigation."""
        page = browser_context

        # Get all navigation radio options
        nav_options = page.locator('div[role="radiogroup"] label').all_text_contents()

        # Verify the order: Home, Contact Us, User Details
        assert nav_options == ["Home", "Contact Us", "User Details"], (
            f"Expected navigation order ['Home', 'Contact Us', 'User Details'], "
            f"but got {nav_options}"
        )

    def test_navigate_to_user_details_page(self, browser_context):
        """Verify user can navigate to User Details page from sidebar."""
        page = browser_context

        # Click on User Details in the sidebar
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Verify the page title
        assert page.locator("h1:has-text('User Details')").is_visible()
        assert page.locator(
            "text=Please share your details so our team can follow up with you."
        ).is_visible()


class TestUserDetailsForm:
    """Test User Details form behavior and validation."""

    def test_form_elements_are_visible(self, browser_context):
        """Verify all form elements are present on User Details page."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Verify form elements - using text-based selectors for Streamlit compatibility
        # Streamlit renders labels and inputs in specific container structures
        assert page.locator('text=Full Name').is_visible()
        assert page.locator('text=Phone Number').is_visible()
        assert page.locator('button:has-text("Submit")').is_visible()

    def test_successful_submission_with_valid_data(
        self, browser_context, clean_user_details_file
    ):
        """Test successful form submission with valid name and phone number."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Fill in the form - using nth input pattern for Streamlit forms
        # Streamlit forms render inputs in order: first Full Name, then Phone Number
        inputs = page.locator('input[type="text"]')
        inputs.nth(0).fill("Jane Doe")
        inputs.nth(1).fill("+1 555-123-4567")

        # Submit the form
        page.locator('button:has-text("Submit")').click()

        # Verify success message
        success_message = page.locator(
            "text=Thank you, Jane Doe! We have received your details."
        )
        assert success_message.is_visible(timeout=5000)

        # Verify data was saved to CSV
        data_file = Path(__file__).parent.parent / "data" / "user_details.csv"
        assert data_file.exists()

        with open(data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["name"] == "Jane Doe"
            assert rows[0]["phone"] == "+1 555-123-4567"
            assert "timestamp" in rows[0]

    def test_submission_with_name_containing_whitespace(
        self, browser_context, clean_user_details_file
    ):
        """Test that names with leading/trailing whitespace are trimmed before saving."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Fill in the form with whitespace
        inputs = page.locator('input[type="text"]')
        inputs.nth(0).fill("  Ann Lee  ")
        inputs.nth(1).fill("1234567")

        # Submit the form
        page.locator('button:has-text("Submit")').click()

        # Verify success message with trimmed name
        success_message = page.locator(
            "text=Thank you, Ann Lee! We have received your details."
        )
        assert success_message.is_visible(timeout=5000)

        # Verify trimmed data in CSV
        data_file = Path(__file__).parent.parent / "data" / "user_details.csv"
        with open(data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]["name"] == "Ann Lee"


class TestUserDetailsFormValidation:
    """Test form validation for User Details page."""

    def test_error_when_name_is_empty(self, browser_context, clean_user_details_file):
        """Test that submitting with empty name shows error message."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Fill only phone number, leave name empty
        inputs = page.locator('input[type="text"]')
        inputs.nth(1).fill("+1 555-123-4567")

        # Submit the form
        page.locator('button:has-text("Submit")').click()

        # Verify error message
        error_message = page.locator("text=Please enter your name.")
        assert error_message.is_visible(timeout=5000)

        # Verify no data was saved
        data_file = Path(__file__).parent.parent / "data" / "user_details.csv"
        assert not data_file.exists()

    def test_error_when_phone_is_empty(self, browser_context, clean_user_details_file):
        """Test that submitting with empty phone shows error message."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Fill only name, leave phone empty
        inputs = page.locator('input[type="text"]')
        inputs.nth(0).fill("John Smith")

        # Submit the form
        page.locator('button:has-text("Submit")').click()

        # Verify error message
        error_message = page.locator("text=Please enter your phone number.")
        assert error_message.is_visible(timeout=5000)

        # Verify no data was saved
        data_file = Path(__file__).parent.parent / "data" / "user_details.csv"
        assert not data_file.exists()

    def test_error_when_phone_is_invalid(
        self, browser_context, clean_user_details_file
    ):
        """Test that submitting with invalid phone format shows error message."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Fill with invalid phone number
        inputs = page.locator('input[type="text"]')
        inputs.nth(0).fill("Mark Twain")
        inputs.nth(1).fill("abc123")

        # Submit the form
        page.locator('button:has-text("Submit")').click()

        # Verify error message
        error_message = page.locator("text=Please enter a valid phone number.")
        assert error_message.is_visible(timeout=5000)

        # Verify no data was saved
        data_file = Path(__file__).parent.parent / "data" / "user_details.csv"
        assert not data_file.exists()

    def test_error_when_phone_is_too_short(
        self, browser_context, clean_user_details_file
    ):
        """Test that phone numbers with less than 7 digits are rejected."""
        page = browser_context

        # Navigate to User Details
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()

        # Fill with too-short phone number (6 digits)
        inputs = page.locator('input[type="text"]')
        inputs.nth(0).fill("Alice Smith")
        inputs.nth(1).fill("123456")

        # Submit the form
        page.locator('button:has-text("Submit")').click()

        # Verify error message
        error_message = page.locator("text=Please enter a valid phone number.")
        assert error_message.is_visible(timeout=5000)


class TestUserDetailsE2E:
    """End-to-end tests for User Details page flow."""

    def test_complete_navigation_flow(
        self, browser_context, clean_user_details_file
    ):
        """Test complete navigation flow: Home -> Contact Us -> User Details."""
        page = browser_context

        # Verify we start on Home page
        assert page.locator("h1:has-text('Enterprise AI Platform')").is_visible()

        # Navigate to Contact Us
        page.locator('div[role="radiogroup"] label:has-text("Contact Us")').click()
        assert page.locator("h1:has-text('Contact Us')").is_visible()
        assert page.locator("text=support@example.com").is_visible()

        # Navigate to User Details (appears after Contact Us)
        page.locator('div[role="radiogroup"] label:has-text("User Details")').click()
        assert page.locator("h1:has-text('User Details')").is_visible()

        # Submit the form
        inputs = page.locator('input[type="text"]')
        inputs.nth(0).fill("John Smith")
        inputs.nth(1).fill("(555) 987-6543")
        page.locator('button:has-text("Submit")').click()

        # Verify success
        success_message = page.locator(
            "text=Thank you, John Smith! We have received your details."
        )
        assert success_message.is_visible(timeout=5000)

        # Verify data persistence
        data_file = Path(__file__).parent.parent / "data" / "user_details.csv"
        assert data_file.exists()

        with open(data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["name"] == "John Smith"
            assert rows[0]["phone"] == "(555) 987-6543"
