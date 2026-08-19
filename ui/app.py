import re

import streamlit as st

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
    st.write("Please enter your details below.")

    with st.form("user_details_form"):
        name = st.text_input("Name")
        phone_number = st.text_input("Phone Number")
        submitted = st.form_submit_button("Submit")

    if submitted:
        errors = []

        if not name.strip():
            errors.append("Name is required.")

        if not phone_number.strip():
            errors.append("Phone number is required.")
        elif not re.fullmatch(r"[0-9+\-\s]{7,15}", phone_number.strip()):
            errors.append("Please enter a valid phone number.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success(f"Thank you, {name.strip()}! Your details have been submitted.")


if page == "Home":
    render_home()
elif page == "Contact Us":
    render_contact_us()
elif page == "User Details Form":
    render_user_details_form()
