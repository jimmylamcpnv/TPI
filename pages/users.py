import streamlit as st
from utils.auth import require_role

# ── Guard ──────────────────────────────────────────
require_role(["admin"])

st.write("hi")