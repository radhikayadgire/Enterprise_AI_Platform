"""
Enterprise AI Platform - Streamlit UI

Pages:
  - Home         : landing page / overview
  - Contact Us    : general contact form
  - User Details  : (MT-5) form shown after Contact Us where a user enters
                    their name and phone number

Run with:
    streamlit run ui/app.py
"""

import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st

APP_TITLE = "Enterprise AI Platform"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USER_DETAILS_CSV = os.path.join(DATA_DIR, "user_details.csv")
USER_DETAILS_COLUMNS = ["timestamp", "name", "phone_number"]

PHONE_PATTERN = re.compile(r"^\+?[0-9\s-]{7,15}$")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_user_details() -> pd.DataFrame:
    if os.path.exists(USER_DETAILS_CSV):
        try:
            return pd.read_csv(USER_DETAILS_CSV)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=USER_DETAILS_COLUMNS)
    return pd.DataFrame(columns=USER_DETAILS_COLUMNS)


def _save_user_detail(name: str, phone_number: str) -> None:
    _ensure_data_dir()
    df = _load_user_details()
    new_row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "name": name.strip(),
        "phone_number": phone_number.strip(),
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(USER_DETAILS_CSV, index=False)


def render_home() -> None:
    st.title(APP_TITLE)
    st.write(
        "Welcome to the Enterprise AI Platform. Use the navigation on the "
        "left to reach the Contact Us page or submit your user details."
    )


def render_contact_us() -> None:
    st.title("Contact Us")
    st.write("Have a question or feedback? Send us a message below.")

    with st.form("contact_us_form", clear_on_submit=True):
        contact_name = st.text_input("Name")
        contact_email = st.text_input("Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Send Message")

    if submitted:
        if not contact_name.strip() or not contact_email.strip() or not message.strip():
            st.error("Please fill in all fields before submitting.")
        else:
            st.success("Thanks for reaching out! We'll get back to you soon.")

    st.info("Next step: head to **User Details** in the sidebar to share your name and phone number.")


def render_user_details() -> None:
    st.title("User Details")
    st.write("Please enter your name and phone number below.")

    with st.form("user_details_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        phone_number = st.text_input("Phone Number", placeholder="e.g. +1 555-123-4567")
        submitted = st.form_submit_button("Submit")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Name is required.")
        if not phone_number.strip():
            errors.append("Phone number is required.")
        elif not PHONE_PATTERN.match(phone_number.strip()):
            errors.append(
                "Phone number must contain 7-15 digits and may include spaces, "
                "hyphens, or a leading +."
            )

        if errors:
            for error in errors:
                st.error(error)
        else:
            _save_user_detail(name, phone_number)
            st.success(f"Thank you, {name.strip()}! Your details have been saved.")

    existing = _load_user_details()
    if not existing.empty:
        st.subheader("Submitted Details")
        st.dataframe(existing, width="stretch")


PAGES = {
    "Home": render_home,
    "Contact Us": render_contact_us,
    "User Details": render_user_details,
}


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":office:", layout="centered")
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", list(PAGES.keys()))
    PAGES[choice]()


main()
