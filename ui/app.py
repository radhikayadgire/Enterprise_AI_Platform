"""Streamlit front-end for the Enterprise AI Platform.

Session handling (IMS-4 fix): the access token's real expiry is derived from
the backend's `expires_in` (seconds) rather than assumed. The token is
proactively refreshed a configurable buffer before it actually expires, so a
slow mobile network round-trip never catches the user mid-expiry and forces
an unexpected logout.
"""
import time

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"
# Refresh the access token once this many seconds remain on it, so a slow
# mobile connection still has margin before the token is rejected.
REFRESH_BUFFER_SECONDS = 60


def _login(username: str, password: str) -> bool:
    resp = requests.post(
        f"{BACKEND_URL}/auth/login",
        data={"username": username, "password": password},
        timeout=10,
    )
    if resp.status_code != 200:
        return False
    _store_session(resp.json())
    return True


def _store_session(token_payload: dict) -> None:
    st.session_state.access_token = token_payload["access_token"]
    st.session_state.refresh_token = token_payload["refresh_token"]
    # expires_in is in seconds and reflects SESSION_TIMEOUT_MINUTES on the
    # backend - do not reinterpret this value, just add it to "now".
    st.session_state.token_expires_at = time.time() + token_payload["expires_in"]


def _ensure_fresh_session() -> bool:
    """Refresh the access token if it's close to expiring. Returns False if
    the session could not be kept alive (refresh token itself expired)."""
    if "access_token" not in st.session_state:
        return False

    if time.time() < st.session_state.token_expires_at - REFRESH_BUFFER_SECONDS:
        return True

    resp = requests.post(
        f"{BACKEND_URL}/auth/refresh",
        json={"refresh_token": st.session_state.refresh_token},
        timeout=10,
    )
    if resp.status_code != 200:
        for key in ("access_token", "refresh_token", "token_expires_at"):
            st.session_state.pop(key, None)
        return False

    _store_session(resp.json())
    return True


def _logout() -> None:
    refresh_token = st.session_state.get("refresh_token")
    if refresh_token:
        try:
            requests.post(f"{BACKEND_URL}/auth/logout", json={"refresh_token": refresh_token}, timeout=10)
        except requests.RequestException:
            pass
    for key in ("access_token", "refresh_token", "token_expires_at"):
        st.session_state.pop(key, None)


def main() -> None:
    st.set_page_config(page_title="Enterprise AI Platform")
    st.title("Enterprise AI Platform")

    if not _ensure_fresh_session():
        st.subheader("Log in")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Log in"):
            if _login(username, password):
                st.rerun()
            else:
                st.error("Invalid username or password.")
        return

    st.sidebar.success("Signed in")
    if st.sidebar.button("Log out"):
        _logout()
        st.rerun()

    message = st.text_input("Ask HR, search docs, or send an email")
    if st.button("Send") and message:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        resp = requests.post(f"{BACKEND_URL}/chat", json={"message": message}, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            st.markdown(f"**{data['agent']}**")
            st.write(data["response"])
        elif resp.status_code == 401:
            st.warning("Your session expired. Please log in again.")
            _logout()
        else:
            st.error(f"Request failed: {resp.status_code}")


if __name__ == "__main__":
    main()
