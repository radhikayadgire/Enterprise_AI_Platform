"""Streamlit UI entry point for the Enterprise AI Platform."""

import streamlit as st

st.set_page_config(page_title="Enterprise AI Platform", layout="wide")


def render_home():
    st.title("Enterprise AI Platform")
    st.write("Welcome to the Enterprise AI Platform.")


def render_contact_us():
    st.title("Contact Us")
    st.write("We'd love to hear from you. Reach out using the details below.")

    st.subheader("Address")
    st.write("ABC park, Pune")


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Contact Us"])

    if page == "Home":
        render_home()
    elif page == "Contact Us":
        render_contact_us()


if __name__ == "__main__":
    main()
