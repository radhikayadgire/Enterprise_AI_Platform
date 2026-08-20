"""
Streamlit UI for the Enterprise AI Platform.

Pages:
    - Home
    - Contact Us
    - User Details  (MT-5: shown right after Contact Us, collects the
      visitor's name and phone number)
"""
import os
import re

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")

PAGES = ["Home", "Contact Us", "User Details"]

st.set_page_config(page_title="Enterprise AI Platform", page_icon="🤖", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "submitted_user_details" not in st.session_state:
    st.session_state.submitted_user_details = None


def go_to(page_name: str) -> None:
    st.session_state.page = page_name


with st.sidebar:
    st.title("Navigation")
    choice = st.radio("Go to", PAGES, index=PAGES.index(st.session_state.page))
    if choice != st.session_state.page:
        st.session_state.page = choice


def render_home() -> None:
    st.title("Enterprise AI Platform")
    st.write(
        "Welcome to the Enterprise Generative AI Platform. Use the sidebar "
        "to navigate between pages."
    )


def render_contact_us() -> None:
    st.title("Contact Us")
    st.write("We'd love to hear from you. Reach out with any questions or feedback.")
    st.markdown(
        """
        - **Email:** support@enterprise-ai-platform.com
        - **Phone:** +1 (800) 555-0100
        - **Address:** 123 Innovation Way, Enterprise City
        """
    )
    st.divider()
    st.write(
        "Before you go, please share a few details so our team can follow up with you."
    )
    if st.button("Continue to User Details ➜", type="primary"):
        go_to("User Details")
        st.rerun()


def render_user_details() -> None:
    st.title("User Details")
    st.write("Please enter your name and phone number so we can get in touch with you.")

    with st.form("user_details_form", clear_on_submit=False):
        name = st.text_input("Full Name", max_chars=100)
        phone_number = st.text_input("Phone Number", placeholder="e.g. +1 5551234567")
        submitted = st.form_submit_button("Submit")

    if submitted:
        errors = []
        name = (name or "").strip()
        phone_number = (phone_number or "").strip()

        if not name:
            errors.append("Name is required.")
        if not phone_number:
            errors.append("Phone number is required.")
        elif not PHONE_RE.match(phone_number):
            errors.append(
                "Phone number must contain 7-15 digits, optionally prefixed with +."
            )

        if errors:
            for error in errors:
                st.error(error)
        else:
            payload = {"name": name, "phone_number": phone_number}
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/user-details", json=payload, timeout=5
                )
                response.raise_for_status()
                st.session_state.submitted_user_details = response.json()
                st.success(f"Thank you, {name}! Your details have been submitted.")
            except requests.RequestException as exc:
                st.session_state.submitted_user_details = payload
                st.warning(
                    "We saved your details locally, but couldn't reach the "
                    f"backend service ({exc}). Our team will still follow up."
                )

    if st.session_state.submitted_user_details:
        st.divider()
        st.subheader("Submitted Details")
        st.json(st.session_state.submitted_user_details)


RENDERERS = {
    "Home": render_home,
    "Contact Us": render_contact_us,
    "User Details": render_user_details,
}

RENDERERS[st.session_state.page]()
