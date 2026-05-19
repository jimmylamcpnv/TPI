import streamlit as st
from utils.supabase import *
import plotly.express as px
from utils.auth import require_role
import pandas as pd

# ── Guard ──────────────────────────────────────────
require_role(["admin", "standard"])
st.write("role:", st.session_state.get("role"))
st.write("logged_in:", st.session_state.get("logged_in"))

# ── Data ──────────────────────────────────────────────
all_equipments = global_search(None)
all_users = get_user_info(None)

# transform into a structure table
df = pd.DataFrame(all_equipments)

# ───── Equipements ──────────────────────────────────────────
# ── Stat / if admin ───────────────────────────────────────────
if st.session_state.role == "admin":
    st.page_link("pages/equipments.py", label="Equipments", icon="🖥️")
else:
    st.markdown("### 🖥️ Equipments")

col1, col2, col3, col4, col5 = st.columns(5, border=True)

col1.metric("Total", len(all_equipments))
col2.metric("Active", len([device for device in all_equipments if device["status"] == "active"]))
col3.metric("In stock", len([device for device in all_equipments if device["status"] == "in_stock"]))
col4.metric("In repair", len([device for device in all_equipments if device["status"] == "in_repair"]))
col5.metric("Expired", len([device for device in all_equipments if device["status"] == "expired"]))
        
# ── Statistics ──────────────────────────────────────
col1, col2 = st.columns(2, border=True)
# repartition par type (desktop, laptop, mobile etc..)
with col1:
    df_type = df.groupby("type").size().reset_index(name="count")
    fig_type = px.bar(
        df_type,
        x="type",
        y="count",
        title="Type of equipment",
        color="type"
    )
    st.plotly_chart(fig_type, use_container_width=True)

# status (camembert)
with col2:
    df_status = df.groupby("status").size().reset_index(name="count")
    fig_status = px.pie(
        df_status,
        names="status",
        values="count",
        title="Status"
    )
    st.plotly_chart(fig_status, use_container_width=True)

# ── Display equipments ──────
with st.container(border=False, height=300):
    for device in all_equipments:
        status_color = {
            "active": "#22c55e",
            "in_stock": "#3b82f6",
            "in_repair": "#f59e0b",
            "retired": "#6b7280"
        }.get(device["status"], "#6b7280") # .get() if no status found, gray

        st.markdown(f"""
        <div style="
            border: 1px solid #2d2d2d;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="display:flex; align-items:center; gap:16px;">
                <div>
                    <strong style="font-size:1rem;">{device["name"]}</strong>
                    <span style="color:#888; font-size:0.8rem; margin-left:8px;">{device["brand"]} · {device["model"]}</span>
                    <br>
                    <span style="color:#aaa; font-size:0.75rem;">SN: {device["serial_number"]} · {device["type"]}</span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="
                    background:{status_color}22;
                    color:{status_color};
                    border:1px solid {status_color};
                    border-radius:20px;
                    padding:2px 10px;
                    font-size:0.75rem;
                ">{device["status"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ───── Users ─────────────────────────────────────────────────
# ── Stat / if admin ────────────────────────────────────
if st.session_state.role == "admin":
    st.page_link("pages/users.py", label="Users", icon="🙎‍♂️")
else:
    st.markdown("###🙎‍♂️ Users management")

# ── Display users ──────
with st.container(border=False, height=300):
    for user in all_users:
        role_color = {
            "admin": "#f59e0b",
            "standard": "#3b82f6",
        }.get(user["role"], "#6b7280")

        st.markdown(f"""
        <div style="
            border: 1px solid #2d2d2d;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="display:flex; align-items:center; gap:16px;">
                <div>
                    <strong style="font-size:1rem;">{user["username"]}</strong>
                </div>
            </div>
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
        </div>
        """, unsafe_allow_html=True)

# garanties (liste de ceux qui vont bientot exiprer)

# Tableau des dernières actions (logs) avec type d'action, utilisateur, date/heure

st.divider()