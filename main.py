"""
Author      : Jimmy LAM
Title       : Serial Guard
github      : https://github.com/jimmylamcpnv/TPI
Version     : V2
Description : 

    Serial Guard v2 is a web-based IT asset management application built with Streamlit and Supabase.

    It allows organizations to track, manage, and maintain their IT equipment in a structured and reliable way.

    Key features:
    - Equipment management (add, edit, delete, search by serial number or type)
    - OCR-powered serial number recognition from uploaded images (doctr)
    - Role-based access control (Administrator / Standard User)
    - Action logging and audit trail
    - Warranty tracking and CSV export
    - Interactive dashboard with real-time statistics
"""
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from utils.auth import *

# ── Session ────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# ── Cookies ────────────────────────────────────────
# initialize the cookies manager
cookies = EncryptedCookieManager(prefix="serialguard_", password="secret123")

# if cookies is not raedy, the rest of the script doesn't load
if not cookies.ready():
    st.stop()

# current page
current_page = cookies.get("current_page") or "pages/dashboard.py"

# if already logged in is in the cookies
if cookies.get("logged_in") == "true":
    st.session_state.logged_in = True
    st.session_state.role = cookies.get("role")
    st.session_state.username = cookies.get("username")

# ── Navigation ────────────────────────────────────────
if not st.session_state.logged_in :
    pg = st.navigation([
        st.Page("pages/welcome.py", title="Login")
        ])

elif st.session_state.role == "admin":
    pg = st.navigation([
        st.Page("pages/dashboard.py", title="Dashboard"),
        st.Page("pages/users.py", title="Users management"),
        st.Page("pages/equipments.py", title="Equipments management"),
        st.Page("pages/logs.py", title="Logs"),
        st.Page("pages/parameters.py", title="Parameters", visibility="hidden")
    ])

elif st.session_state.role == "standard":
    pg = st.navigation([
        st.Page("pages/dashboard.py", title="Dashboard"),
        st.Page("pages/parameters.py", title="Parameters", visibility="hidden")
    ])
elif st.session_state.logged_in :
    pg = st.navigation([
        st.Page("pages/dashboard.py", title="Dashboard"),
        st.Page("pages/parameters.py", title="Parameters", visibility="hidden")
    ])

# ── Sidebar ────────────────────────────────────────
# Displayed login button
with st.sidebar:
    if st.session_state.logged_in:
        col1, col2 = st.columns([2, 2], vertical_alignment="center")
        with col1:
            st.caption(f"👤 **{st.session_state.username}** / {st.session_state.role}")

        with col2:
            if st.button("logout", icon="🚪", type="primary"):
                # session state
                st.session_state.logged_in = False
                st.session_state.role = None

                # cookies
                cookies["logged_in"] = ""
                cookies["role"] = ""
                cookies["username"] = ""
                cookies.save()

                st.rerun()
                
        with st.container():
            st.page_link("pages/parameters.py", label="Parameters", icon="⚙️")
    else:
        if st.button("login", icon="🔐"):
            login_dialog(cookies)

pg.run()