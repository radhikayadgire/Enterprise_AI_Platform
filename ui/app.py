"""Streamlit entrypoint for the Enterprise AI Platform, starting with user login."""
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Enterprise AI Platform", page_icon="🔐", layout="centered")

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "username" not in st.session_state:
    st.session_state.username = None


def login(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": username, "password": password},
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach the backend: {exc}")
        return False

    if response.status_code == 200:
        st.session_state.access_token = response.json()["access_token"]
        st.session_state.username = username
        return True

    detail = response.json().get("detail", "Login failed") if response.content else "Login failed"
    st.error(detail)
    return False


def register(username: str, email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach the backend: {exc}")
        return False

    if response.status_code == 201:
        st.success("Account created. You can now log in.")
        return True

    detail = response.json().get("detail", "Registration failed") if response.content else "Registration failed"
    st.error(detail)
    return False


def logout():
    st.session_state.access_token = None
    st.session_state.username = None


def render_login_page():
    st.title("Enterprise AI Platform")
    st.subheader("Sign in to continue")

    login_tab, register_tab = st.tabs(["Login", "Create account"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif login(username, password):
                    st.rerun()

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Username", key="register_username")
            new_email = st.text_input("Email", key="register_email")
            new_password = st.text_input("Password", type="password", key="register_password")
            register_submitted = st.form_submit_button("Create account")
            if register_submitted:
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields.")
                else:
                    register(new_username, new_email, new_password)


def render_app():
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Log out"):
        logout()
        st.rerun()

    st.title("Enterprise AI Platform")
    st.write(f"Welcome, **{st.session_state.username}**! You are now signed in.")


if st.session_state.access_token:
    render_app()
else:
    render_login_page()
