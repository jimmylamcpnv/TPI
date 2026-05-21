import streamlit as st
from utils.auth import require_role
from utils.supabase.db_equipements import *
from pages.ocr import *

# ── Session ──────────────────────────────────────────
require_role(["admin"])

# ── Data ──────────────────────────────────────────
all_users = get_user_info(None)

# ── Functions ──────────────────────────────────────────
# ── add manually
@st.dialog("Add user manually")
def add_user_manually():
    username = st.text_input("Entet a username*")
    password = st.text_input("Enter a password*", type="password")
    confirm_password = st.text_input("Confirm your password*", type="password")
    
    # if the password is not the same
    if password != confirm_password:
        st.warning("password not the same")
        st.stop()

    # checkbox to make the user admin or not
    role = "admin" if st.checkbox("Admin") else "standard"

    if st.button(label="Submit"):
        errors = []
        try:
            create_user(username, password, role)
            st.success(f"{username} has been added to supabase !")

        except ValueError as error:
            errors.append(str(error))
            st.error(errors)
        # mettre des logs de l'erreur

# ── edit user datas
@st.dialog("Edit user datas")
def edit_user(user):
    with st.container(border=True):
        new_username = st.text_input("Username", value = user["username"])
        new_role = "admin" if st.checkbox("Admin", value = user["role"] == "admin") else "standard" # user["role"] == "admin" return True or False
    
    # button save
    with st.container(border=False, horizontal_alignment="right"):
        if st.button("Save"):
            errors = []
            try:
                update_user(user["username"], new_username, new_role)
                st.success("modifications has been saved successfully")

            except ValueError as error:
                errors.append(str(error))
                st.error(errors)

# ── show user infos
@st.dialog("Show user infos")
def show_user_info(user):

    role_color = {
        "admin": "orange",
        "standard": "blue",
    }.get(user["role"], "gray")

    # container for username and role
    with st.container(horizontal=True):
        st.subheader((user["username"]))
        st.badge(user["role"], color=role_color)

    # container for logs
    with st.container(border=True):
        st.subheader("Logs")

        logs = supabase.table("activity_logs") \
            .select("*, equipments(name)") \
            .eq("user_id", user["id"]) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute().data

        if not logs:
            st.caption("nothing here")

        for log in logs:
            equipment  = log["equipments"]["name"] if log["equipments"] else "—"
            log_date   = log["created_at"][:16].replace("T", " ")
            action     = log["action"]
            details    = log["details"] or {}
            details_str = "  ·  ".join(f"{k} : {v}" for k, v in details.items())
            st.caption(f"{log_date}  ·  {action}  ·  {equipment}  ·  {details_str}")
    
    # container for buttons
    with st.container(horizontal=True):
        # delete button
        with st.container(horizontal_alignment="left"):
            if st.button("Delete", type="primary"):
                errors = []
                try:
                    delete_user(user["username"])
                    st.success(f"User {user["username"]} has been deleted")

                except ValueError as error:
                    errors.append(error)
                    st.error(errors)
        
        # edit button
        with st.container(horizontal_alignment="right"):
            if st.button("Edit"):
                st.session_state["edit_user_target"] = user
                st.rerun()

# store user's data of edited user, not the logged one
if "edit_user_target" in st.session_state:
    user_to_edit = st.session_state.pop("edit_user_target")
    edit_user(user_to_edit)

# ── Header / Buttons ──────────────────────────────────────────
col_title, col1 = st.columns([8, 1.8], vertical_alignment="center")

with col_title:
    st.markdown("<p style='font-size:2rem; margin:0; font-weight:bold'>🙎‍♂️ Users</p>", unsafe_allow_html=True)
    st.markdown(f"<small>Total users : {len(all_users)}</small>", unsafe_allow_html=True)

with col1:
    if st.button("Add user", type="secondary", width=100):
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
                show_user_info(user)