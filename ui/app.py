import streamlit as st

st.set_page_config(page_title="Contact Us", page_icon="📇")

st.title("Contact Us")

st.write("Reach out to us using the details below.")

st.text_input("Name", value="Radhika", disabled=True)
st.text_input("Phone Number", value="87382782", disabled=True)
