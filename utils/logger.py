import streamlit as st
from utils.supabase.db_connexion import supabase

def log_action(action: str, equipment_id: int = None, details=None):
    # Accepte string or dict for details
    if isinstance(details, str):
        details = {"message": details}
    
    supabase.table("activity_logs").insert({
        "user_id":      st.session_state.get("user_id"),
        "equipment_id": equipment_id,
        "action":       action,
        "details":      details or {}
    }).execute()