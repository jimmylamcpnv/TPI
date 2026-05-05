import streamlit as st
import bcrypt
from utils.supabase.db_users import *

"""
Prendre username et password en entrée
Chercher l'utilisateur dans Supabase par username
Comparer le mot de passe avec password_hash
Si OK → mettre à jour st.session_state
"""
@st.dialog("Login")
def login_dialog(cookies):
    # text input
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")
    
    if st.button("login"):
        # fetch user data from supabase
        user = get_user_info(username_input)

        # if user data is not empty
        if user:
            # convert the hash form supabase to bytes
            password_hash = user[0]["password_hash"].encode("utf-8")
            
            # compare if it correspond
            if bcrypt.checkpw(password_input.encode("utf-8"), password_hash):
                # session state
                st.session_state.logged_in = True
                st.session_state.role = user[0]["role"]
                st.session_state.username = user[0]["username"]

                # cookies
                cookies["logged_in"] = "true"
                cookies["role"] = user[0]["role"]
                cookies["username"] = user[0]["username"]

                st.success("You are now log in")
                st.rerun()
            else:
                st.error("Password is incorrect")
        else:
            st.error("username is incorrect or does not exist.")

# function to allow navigation
def require_role(allowed_roles: list):
    # if not logged
    if not st.session_state.get("logged_in"):
        st.error("You must be logged in to access this page.")
        st.stop()

    # if not role allowed
    if st.session_state.role not in allowed_roles:
        st.error("You don't have permission to access this page.")
        st.stop()
