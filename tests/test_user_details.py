"""Automation tests for User Details form functionality."""
import pytest
from playwright.sync_api import Page, expect


class TestUserDetailsForm:
    """Test suite for User Details form on the Streamlit app."""

    def navigate_to_user_details(self, page: Page) -> None:
        """Helper method to navigate to User Details page."""
        # Click on User Details radio button in sidebar
        page.get_by_text("User Details", exact=True).click()
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        # Verify User Details title is visible
        expect(page.get_by_role("heading", name="User Details")).to_be_visible()

    def fill_user_form(self, page: Page, name: str, phone: str) -> None:
        """Helper method to fill the user details form."""
        # Fill name field
        name_input = page.get_by_label("Name")
        name_input.fill(name)

        # Fill phone number field
        phone_input = page.get_by_label("Phone Number")
        phone_input.fill(phone)

    def submit_form(self, page: Page) -> None:
        """Helper method to submit the form."""
        # Click submit button
        submit_button = page.get_by_role("button", name="Submit")
        submit_button.click()
        # Wait for form processing
        page.wait_for_timeout(500)

    @pytest.mark.happy_path
    def test_submit_valid_user_details(self, page: Page) -> None:
        """
        TC-001: Submit User Details form with valid name and phone number.

        Verifies that a user can successfully submit the form with valid data
        and see a success message and their entry in the submitted users table.
        """
        # Navigate to User Details page
        self.navigate_to_user_details(page)

        # Fill form with valid data
        test_name = "John Smith"
        test_phone = "+14155552671"
        self.fill_user_form(page, test_name, test_phone)

        # Submit form
        self.submit_form(page)

        # Verify success message appears
        success_message = f"Thank you, {test_name}! Your details have been submitted."
        expect(page.get_by_text(success_message)).to_be_visible()

        # Verify submitted user appears in table
        expect(page.get_by_role("heading", name="Submitted Users")).to_be_visible()
        expect(page.get_by_text(test_name)).to_be_visible()
        expect(page.get_by_text(test_phone)).to_be_visible()

    @pytest.mark.e2e
    def test_navigate_and_submit_user_details(self, page: Page) -> None:
        """
        TC-002: Navigate from Contact Us to User Details and submit.

        Verifies the complete user flow: Home -> Contact Us -> User Details -> Submit.
        """
        # Verify Home page loads by default
        expect(page.get_by_role("heading", name="Enterprise AI Platform")).to_be_visible()

        # Navigate to Contact Us
        page.get_by_text("Contact Us", exact=True).click()
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", name="Contact Us")).to_be_visible()
        expect(page.get_by_text("support@enterprise-ai-platform.com")).to_be_visible()

        # Navigate to User Details (listed after Contact Us)
        page.get_by_text("User Details", exact=True).click()
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", name="User Details")).to_be_visible()

        # Fill and submit form
        test_name = "Priya Rao"
        test_phone = "9876543210"
        self.fill_user_form(page, test_name, test_phone)
        self.submit_form(page)

        # Verify submission success
        success_message = f"Thank you, {test_name}! Your details have been submitted."
        expect(page.get_by_text(success_message)).to_be_visible()

        # Verify entry in table
        expect(page.get_by_text(test_name)).to_be_visible()
        expect(page.get_by_text(test_phone)).to_be_visible()

    @pytest.mark.edge_case
    def test_submit_minimum_length_phone(self, page: Page) -> None:
        """
        TC-003: Submit phone number at minimum allowed length boundary (7 digits).

        Verifies that a 7-digit phone number (minimum valid length) is accepted.
        """
        self.navigate_to_user_details(page)

        # Fill form with 7-digit phone (minimum valid)
        test_name = "Alex Lee"
        test_phone = "1234567"
        self.fill_user_form(page, test_name, test_phone)
        self.submit_form(page)

        # Verify success
        success_message = f"Thank you, {test_name}! Your details have been submitted."
        expect(page.get_by_text(success_message)).to_be_visible()
        expect(page.get_by_text(test_name)).to_be_visible()

    @pytest.mark.edge_case
    def test_submit_exceeding_max_length_phone(self, page: Page) -> None:
        """
        TC-004: Submit phone number exceeding maximum allowed length (16 digits).

        Verifies that a 16-digit phone number is rejected with appropriate error.
        """
        self.navigate_to_user_details(page)

        # Fill form with 16-digit phone (exceeds maximum)
        test_name = "Sam Park"
        test_phone = "1234567890123456"
        self.fill_user_form(page, test_name, test_phone)
        self.submit_form(page)

        # Verify error message appears
        error_message = "Phone number must contain 7-15 digits (an optional leading '+' is allowed)."
        expect(page.get_by_text(error_message)).to_be_visible()

        # Verify no success message
        expect(page.get_by_text("Thank you")).not_to_be_visible()

        # Verify user table header is not present (no submissions)
        expect(page.get_by_role("heading", name="Submitted Users")).not_to_be_visible()

    @pytest.mark.happy_path
    def test_submit_phone_with_plus_sign(self, page: Page) -> None:
        """
        TC-005: Submit phone number with leading plus sign (international format).

        Verifies that international phone numbers with '+' prefix are accepted.
        """
        self.navigate_to_user_details(page)

        # Fill form with international format phone
        test_name = "Maria Gomez"
        test_phone = "+919876543210"
        self.fill_user_form(page, test_name, test_phone)
        self.submit_form(page)

        # Verify success
        success_message = f"Thank you, {test_name}! Your details have been submitted."
        expect(page.get_by_text(success_message)).to_be_visible()

        # Verify phone with '+' is preserved in table
        expect(page.get_by_text(test_phone)).to_be_visible()

    @pytest.mark.negative
    def test_submit_empty_name(self, page: Page) -> None:
        """
        TC-006: Submit form with empty name field.

        Verifies that submitting with an empty name shows validation error.
        """
        self.navigate_to_user_details(page)

        # Fill only phone number, leave name empty
        self.fill_user_form(page, "", "9876543210")
        self.submit_form(page)

        # Verify error message
        expect(page.get_by_text("Name is required.")).to_be_visible()

        # Verify no success message
        expect(page.get_by_text("Thank you")).not_to_be_visible()

        # Verify no table appears
        expect(page.get_by_role("heading", name="Submitted Users")).not_to_be_visible()

    @pytest.mark.negative
    def test_submit_non_numeric_phone(self, page: Page) -> None:
        """
        TC-007: Submit form with non-numeric phone number.

        Verifies that non-numeric phone numbers are rejected with validation error.
        """
        self.navigate_to_user_details(page)

        # Fill form with alphabetic phone number
        test_name = "Chris Doe"
        test_phone = "abc-defg"
        self.fill_user_form(page, test_name, test_phone)
        self.submit_form(page)

        # Verify error message
        error_message = "Phone number must contain 7-15 digits (an optional leading '+' is allowed)."
        expect(page.get_by_text(error_message)).to_be_visible()

        # Verify no success message
        expect(page.get_by_text("Thank you")).not_to_be_visible()

        # Verify no table appears
        expect(page.get_by_role("heading", name="Submitted Users")).not_to_be_visible()

    @pytest.mark.edge_case
    def test_submit_multiple_users(self, page: Page) -> None:
        """
        Additional test: Submit multiple users and verify all appear in table.

        Verifies that the table correctly accumulates multiple submissions.
        """
        self.navigate_to_user_details(page)

        # Submit first user
        self.fill_user_form(page, "Alice Johnson", "1234567890")
        self.submit_form(page)
        expect(page.get_by_text("Thank you, Alice Johnson!")).to_be_visible()

        # Submit second user
        self.fill_user_form(page, "Bob Williams", "+447700900123")
        self.submit_form(page)
        expect(page.get_by_text("Thank you, Bob Williams!")).to_be_visible()

        # Verify both users in table
        expect(page.get_by_text("Alice Johnson")).to_be_visible()
        expect(page.get_by_text("1234567890")).to_be_visible()
        expect(page.get_by_text("Bob Williams")).to_be_visible()
        expect(page.get_by_text("+447700900123")).to_be_visible()
