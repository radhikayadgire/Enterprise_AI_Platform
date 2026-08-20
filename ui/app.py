import csv
import os
import re
from datetime import datetime, timezone

import streamlit as st

APP_TITLE = "Enterprise AI Platform"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
USER_DETAILS_FILE = os.path.join(DATA_DIR, "user_details.csv")
PHONE_PATTERN = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


def save_user_details(name, phone):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.isfile(USER_DETAILS_FILE)
    with open(USER_DETAILS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "name", "phone"])
        writer.writerow([datetime.now(timezone.utc).isoformat(), name, phone])


def render_home():
    st.title(APP_TITLE)
    st.write(
        "Welcome to the Enterprise AI Platform. Use the navigation on the left "
        "to get started."
    )


def render_contact_us():
    st.title("Contact Us")
    st.write("Have a question? Reach out to our team.")
    st.markdown("**Email:** support@example.com")
    st.markdown("**Phone:** +1 (555) 123-4567")


def render_user_details():
    st.title("User Details")
    st.write("Please share your details so our team can follow up with you.")

    with st.form("user_details_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        submitted = st.form_submit_button("Submit")

    if submitted:
        name = name.strip()
        phone = phone.strip()
        if not name:
            st.error("Please enter your name.")
        elif not phone:
            st.error("Please enter your phone number.")
        elif not PHONE_PATTERN.match(phone):
            st.error("Please enter a valid phone number.")
        else:
            save_user_details(name, phone)
            st.success(f"Thank you, {name}! We have received your details.")


PAGES = {
    "Home": render_home,
    "Contact Us": render_contact_us,
    "User Details": render_user_details,
}


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon=":robot_face:")
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", list(PAGES.keys()))
    PAGES[choice]()


if __name__ == "__main__":
    main()
