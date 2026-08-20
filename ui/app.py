import re

import streamlit as st

PHONE_PATTERN = re.compile(r"^[0-9+\-\s()]{7,20}$")

st.set_page_config(page_title="Enterprise AI Platform", page_icon="🤖", layout="centered")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Contact Us", "User Details Form"])


def render_home():
    st.title("Enterprise AI Platform")
    st.write("Welcome to the Enterprise AI Platform.")


def render_contact_us():
    st.title("Contact Us")
    st.write("We'd love to hear from you. Reach out using the details below.")

    st.subheader("Address")
    st.write("123 Enterprise Avenue, Business Park, Pune, Maharashtra, 411001, India")

    st.subheader("Email")
    st.write("support@enterpriseaiplatform.com")

    st.subheader("Phone")
    st.write("+91 20 1234 5678")


def render_user_details_form():
    st.title("User Details Form")
    st.write("Please share your name and phone number and we'll get back to you.")

    with st.form("user_details_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone_number = st.text_input("Phone Number")
        submitted = st.form_submit_button("Submit")

    if submitted:
        errors = []

        name = name.strip()
        phone_number = phone_number.strip()

        if not name:
            errors.append("Name is required.")

        if not phone_number:
            errors.append("Phone number is required.")
        elif not PHONE_PATTERN.match(phone_number):
            errors.append("Please enter a valid phone number.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success(f"Thank you, {name}! Your details have been submitted.")


PAGES = {
    "Home": render_home,
    "Contact Us": render_contact_us,
    "User Details Form": render_user_details_form,
}

PAGES[page]()
