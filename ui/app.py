import re

import streamlit as st

st.set_page_config(page_title="Enterprise AI Platform", layout="centered")

PAGES = ["Home", "Contact Us", "User Details"]

if "submitted_users" not in st.session_state:
    st.session_state.submitted_users = []

page = st.sidebar.radio("Navigate", PAGES)


def render_home():
    st.title("Enterprise AI Platform")
    st.write("Welcome! Use the sidebar to navigate to Contact Us or User Details.")


def render_contact_us():
    st.title("Contact Us")
    st.write("Have a question or feedback? Reach out to us using the details below.")
    st.write("**Email:** support@enterprise-ai-platform.com")
    st.write("**Phone:** +1 (555) 123-4567")


def render_user_details():
    st.title("User Details")
    st.write("Please enter your details below.")

    with st.form("user_details_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone_number = st.text_input("Phone Number")
        submitted = st.form_submit_button("Submit")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Name is required.")
        if not re.fullmatch(r"\+?\d{7,15}", phone_number.strip()):
            errors.append("Phone number must contain 7-15 digits (an optional leading '+' is allowed).")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state.submitted_users.append(
                {"name": name.strip(), "phone_number": phone_number.strip()}
            )
            st.success(f"Thank you, {name.strip()}! Your details have been submitted.")

    if st.session_state.submitted_users:
        st.subheader("Submitted Users")
        st.table(st.session_state.submitted_users)


if page == "Home":
    render_home()
elif page == "Contact Us":
    render_contact_us()
elif page == "User Details":
    render_user_details()
