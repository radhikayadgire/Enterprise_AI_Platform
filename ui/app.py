"""Streamlit client for the Enterprise AI Platform.

Fix for IMS-4: the client now holds both the access token and the
long-lived refresh token in session state, and transparently exchanges the
refresh token for a new access token whenever a call comes back 401. This
is what keeps a user signed in instead of being logged out the moment the
short-lived access token expires.
"""
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _post(path: str, **kwargs):
    return requests.post(f"{BACKEND_URL}{path}", timeout=10, **kwargs)


def login(username: str, password: str) -> bool:
    response = _post(
        "/api/auth/login",
        data={"username": username, "password": password},
        headers={"X-Device-Type": "mobile"},
    )
    if response.status_code != 200:
        return False
    data = response.json()
    st.session_state.access_token = data["access_token"]
    st.session_state.refresh_token = data["refresh_token"]
    return True


def refresh_access_token() -> bool:
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        return False
    response = _post("/api/auth/refresh", json={"refresh_token": refresh_token})
    if response.status_code != 200:
        # Refresh session itself expired/revoked - the user must log in again.
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)
        return False
    st.session_state.access_token = response.json()["access_token"]
    return True


def authed_get(path: str):
    """GET a protected endpoint, silently refreshing the session on 401."""
    token = st.session_state.get("access_token")
    response = requests.get(
        f"{BACKEND_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if response.status_code == 401 and refresh_access_token():
        token = st.session_state.get("access_token")
        response = requests.get(
            f"{BACKEND_URL}{path}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    return response


def logout() -> None:
    refresh_token = st.session_state.get("refresh_token")
    if refresh_token:
        _post("/api/auth/logout", json={"refresh_token": refresh_token})
    st.session_state.pop("access_token", None)
    st.session_state.pop("refresh_token", None)


def main() -> None:
    st.set_page_config(page_title="Enterprise AI Platform", page_icon="🤖")
    st.title("Enterprise AI Platform")

    if not st.session_state.get("access_token"):
        st.subheader("Log in")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
        if submitted:
            if login(username, password):
                st.rerun()
            else:
                st.error("Incorrect username or password")
        return

    me = authed_get("/api/auth/me")
    if me.status_code != 200:
        st.warning("Your session has expired. Please log in again.")
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)
        st.rerun()
        return

    user = me.json()
    st.success(f"Logged in as {user['username']} ({user['email']})")
    if st.button("Log out"):
        logout()
        st.rerun()


if __name__ == "__main__":
    main()
