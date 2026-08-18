"""Streamlit UI entry point for the Enterprise AI Platform.

Run with:
    streamlit run ui/app.py
"""

import streamlit as st

st.set_page_config(page_title="Enterprise AI Platform", page_icon=":robot_face:")


def render_home():
    st.title("Enterprise AI Platform")
    st.write("Welcome to the Enterprise AI Platform.")


def render_contact_us():
    st.title("Contact Us")
    st.write("Feel free to reach out to us with any questions or feedback.")

    st.subheader("Radhika Yadgire")
    st.write(f"**Phone:** 1234567")
    st.write(f"**Email:** radhika@gmail.com")


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Contact Us"])

    if page == "Home":
        render_home()
    elif page == "Contact Us":
        render_contact_us()


if __name__ == "__main__":
    main()
