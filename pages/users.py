import streamlit as st
from utils.auth import require_role
from utils.supabase.db_equipements import *
from pages.ocr import *

# ── Session ──────────────────────────────────────────
require_role("admin")

# ── Data ──────────────────────────────────────────
all_users = get_user_info(None)

# ── Functions ──────────────────────────────────────────
# add manually
@st.dialog("Add user manually")
def add_user_manually():
    username = st.text_input("Entet a username")
    password = st.text_input("Enter a password")
    confirm_password = st.text_input("Confirm your password")
    role = st.text_input("Choose a role for {username}")

    if st.button(label="Submit"):
        errors = []
        try:
            create_user(
                username,
                password,
                role
                )
            st.success(f"{username} has been added to supabase !")

        except ValueError as error:
            errors.append(str(error))
            st.error(errors)
        # mettre des logs de l'erreur

# show user infos
@st.dialog("Show user infos")
def show_user_info(username):
    st.write(f"Username : {user["username"]}")
    st.write(f"Role : {user["role"]}")

# ── Header / Buttons ──────────────────────────────────────────
col_title, col1 = st.columns([8, 1.8], vertical_alignment="center")

with col_title:
    st.markdown("<p style='font-size:2rem; margin:0; font-weight:bold'>🙎‍♂️ Users</p>", unsafe_allow_html=True)
    st.markdown(f"<small>Total users : {len(all_users)}</small>", unsafe_allow_html=True)

with col1:
    if st.button("Add user", type="primary", width=100):
        add_user_manually()

# ── Search / Filters ──────────────────────────────────────────
with st.container(border=True, vertical_alignment="center", horizontal=True):
    # search_options is the selected options
    search_option = st.text_input("Search")

    all_users = get_user_info(search_option)
    filtered_users = all_users

    # ── Buttons ──────────── 
    # type filter
    role_choice = st.selectbox("Role", ["All", "admin", "standard"], accept_new_options=False)
    if role_choice != "All":
        filtered_users = [user for user in filtered_users if user["role"] == role_choice]

# ── Display filter
with st.container(vertical_alignment="center", horizontal=True):
    st.write(f"Result number : {len(filtered_users)}")
    st.badge(f"Role : {role_choice}")

# ── Display users ──────────────────────────────────────────
for user in filtered_users:
    role_color = {
        "admin": "#f59e0b",
        "standard": "#3b82f6",
    }.get(user["role"], "#6b7280")

    with st.container(border=True):
        col_info, col_role, col_btn = st.columns([6, 2, 1], vertical_alignment="center")

        with col_info:
            st.markdown(f"""
                <strong style="font-size:1rem;">{user["username"]}</strong>
            """, unsafe_allow_html=True)

        with col_role:
            st.markdown(f"""
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="
                        background:{role_color}22;
                        color:{role_color};
                        border:1px solid {role_color};
                        border-radius:20px;
                        padding:2px 10px;
                        font-size:0.75rem;
                    ">{user["role"]}</span>
                </div>
            """, unsafe_allow_html=True)

        with col_btn:
            if st.button("→", key=f"user_{user['id']}"):
                show_user_info(user["username"])