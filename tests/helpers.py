"""
Helper utilities and constants for UI automation tests.
"""
from pathlib import Path


# Selector constants for Streamlit UI elements
class Selectors:
    """Common selectors used across test suite."""

    # Navigation
    RADIO_GROUP = 'div[role="radiogroup"]'
    NAV_LABEL = 'div[role="radiogroup"] label'

    # Form elements
    TEXT_INPUT = 'input[type="text"]'
    SUBMIT_BUTTON = 'button:has-text("Submit")'

    # Pages
    HOME_TITLE = "h1:has-text('Enterprise AI Platform')"
    CONTACT_US_TITLE = "h1:has-text('Contact Us')"
    USER_DETAILS_TITLE = "h1:has-text('User Details')"


# File path helpers
def get_data_file_path(filename):
    """Get the path to a file in the data directory."""
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    return project_root / "data" / filename


def get_user_details_csv_path():
    """Get the path to the user details CSV file."""
    return get_data_file_path("user_details.csv")
