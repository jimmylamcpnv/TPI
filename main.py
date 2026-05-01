"""
Author      : Jimmy LAM
Title       : Serial Guard
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

def dashboard():
    st.title("Dashboard")

def users():
    st.title("Users")

def equipements():
    st.title("Equipements")

def logs():
    st.title("Logs")

pg = st.navigation([
    st.Page(dashboard, title="Dashboard"),
    st.Page(users, title="Users management"),
    st.Page(equipements, title="Equipements management"),
    st.Page(logs, title="Logs")
])

pg.run()
# Displayed pages based on the role
# standard
# admin