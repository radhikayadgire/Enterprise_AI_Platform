"""Streamlit front-end for the Enterprise AI Platform."""

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Enterprise AI Platform", page_icon=":office:")

page = st.sidebar.radio("Navigate", ["Home", "Contact Us", "User Details"])

if page == "Home":
    st.title("Enterprise AI Platform")
    st.write("Ask HR questions, search company policies, and reach the team.")

elif page == "Contact Us":
    st.title("Contact Us")
    st.write("Reach the Enterprise AI Platform team at support@example.com.")

elif page == "User Details":
    st.title("User Details")
    st.write("Tell us a bit about yourself and we'll get back to you.")

    with st.form("user_details_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone number")
        message = st.text_area("Message (optional)")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not name or not email:
            st.error("Name and email are required.")
        else:
            payload = {"name": name, "email": email, "phone": phone, "message": message}
            try:
                response = requests.post(f"{BACKEND_URL}/api/user", json=payload, timeout=5)
                response.raise_for_status()
                st.success(f"Thanks, {name}! We've received your details.")
            except requests.RequestException:
                st.warning(
                    f"Thanks, {name}! Your details were captured locally "
                    "(backend not reachable)."
                )
