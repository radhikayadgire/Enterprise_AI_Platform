"""Streamlit UI entry point for the Enterprise AI Platform.

Adds a "Contact Us" page as requested in MT-2.
"""

import streamlit as st

CONTACT_NAME = "Radhika"
CONTACT_PHONE = "1234567"
CONTACT_EMAIL = "radhika@gmail.com"

st.set_page_config(page_title="Enterprise AI Platform", page_icon="🤖", layout="centered")


def render_home() -> None:
    st.title("Enterprise AI Platform")
    st.write("Welcome to the Enterprise AI Platform. Use the navigation on the left to get around.")


def render_contact_us() -> None:
    st.title("Contact Us")
    st.write("Have a question or need support? Reach out to us using the details below.")

    st.markdown(
        f"""
        **Name:** {CONTACT_NAME}

        **Phone:** {CONTACT_PHONE}

        **Email:** {CONTACT_EMAIL}
        """
    )


def main() -> None:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Home", "Contact Us"))

    if page == "Home":
        render_home()
    elif page == "Contact Us":
        render_contact_us()


if __name__ == "__main__":
    main()
