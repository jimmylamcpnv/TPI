import streamlit as st

st.title("Welcome to Serial Guard v2")

if st.session_state.logged_in == False:
    st.warning("please log you in to use this web app")