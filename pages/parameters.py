import streamlit as st
from utils.supabase.db_users import update_user, update_password, get_user_info
from utils.auth import require_role

# ── Session ──────────────────────────────────────────
require_role(["admin", "standard"])

# ── Header ──────────────────────────────────────────
st.markdown("<p style='font-size:2rem; margin:0; font-weight:bold'>⚙️ Parameters</p>", unsafe_allow_html=True)
st.markdown(f"<small>Logged in as : {st.session_state.username}</small>", unsafe_allow_html=True)

st.write("")

# ── Change username ──────────────────────────────────────────
with st.container(border=True):
    st.subheader("Change username")

    new_username = st.text_input("New username", placeholder=st.session_state.username)

    with st.container(horizontal_alignment="right"):
        if st.button("Save username", type="secondary"):
            errors = []
            try:
                update_user(st.session_state.username, new_username, st.session_state.role)
                st.session_state.username = new_username
                st.success("Username updated successfully")
            except ValueError as error:
                errors.append(str(error))
                st.error(errors)

st.write("")

# ── Change password ──────────────────────────────────────────
with st.container(border=True):
    st.subheader("Change password")

    new_password        = st.text_input("New password", type="password")
    confirm_password    = st.text_input("Confirm new password", type="password")

    if new_password and new_password != confirm_password:
        st.warning("Passwords do not match")

    with st.container(horizontal_alignment="right"):
        if st.button("Save password", type="secondary"):
            errors = []
            if new_password != confirm_password:
                st.error("Passwords do not match")
            elif not new_password:
                st.error("Password cannot be empty")
            else:
                try:
                    update_password(st.session_state.username, new_password)
                    st.success("Password updated successfully")
                except ValueError as error:
                    errors.append(str(error))
                    st.error(errors)