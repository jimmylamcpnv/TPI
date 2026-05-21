import streamlit as st
from utils.supabase import *
import plotly.express as px
from utils.auth import require_role
import pandas as pd
from datetime import date, timedelta
from utils.supabase.db_connexion import supabase

# ── Guard ──────────────────────────────────────────
require_role(["admin", "standard"])

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

if df.empty or "type" not in df.columns or "status" not in df.columns:
    with col1:
        st.caption("No data to display")
    with col2:
        st.caption("No data to display")
else:
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

    with col2:
        df_status = df.groupby("status").size().reset_index(name="count")
        fig_status = px.pie(
            df_status,
            names="status",
            values="count",
            title="Status"
        )
        st.plotly_chart(fig_status, use_container_width=True)

# ───── Display Warranties expiring soon ──────────────────────────────
st.markdown("<p style='font-size:1.3rem; font-weight:bold; margin:0'>⚠️ Warranties expiring soon</p>", unsafe_allow_html=True)
st.markdown("<small>Devices whose warranty expires within the next 90 days</small>", unsafe_allow_html=True)

st.write("")

today       = date.today()
soon        = today + timedelta(days=90)

expiring = []
for device in all_equipments:
    try:
        purchase    = date.fromisoformat(device["purchase_date"])
        months      = int(device["warranty_months"] or 0)
        expiry      = purchase + timedelta(days=months * 30)

        if today <= expiry <= soon:
            days_left = (expiry - today).days
            expiring.append({**device, "expiry_date": expiry, "days_left": days_left})
    except (TypeError, ValueError):
        continue

with st.container(border=True):
    if not expiring:
        st.caption("No warranties expiring in the next 90 days")
    else:
        for device in sorted(expiring, key=lambda x: x["days_left"]):
            urgency_color = "#ef4444" if device["days_left"] <= 30 else "#f59e0b"

            st.markdown(f"""
            <div style="
                border: 1px solid {urgency_color}55;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            ">
                <div>
                    <strong style="font-size:1rem;">{device["name"]}</strong>
                    <span style="color:#888; font-size:0.8rem; margin-left:8px;">{device["brand"]} · {device["model"]}</span>
                    <br>
                    <span style="color:#aaa; font-size:0.75rem;">SN: {device["serial_number"]} · expires {device["expiry_date"]}</span>
                </div>
                <span style="
                    background:{urgency_color}22;
                    color:{urgency_color};
                    border:1px solid {urgency_color};
                    border-radius:20px;
                    padding:2px 10px;
                    font-size:0.75rem;
                ">{device["days_left"]} days left</span>
            </div>
            """, unsafe_allow_html=True)

# ── Display equipments ──────
with st.container(border=False, height=300):
    for device in all_equipments:
        status_color = {
            "active": "#22c55e",
            "in_stock": "#3b82f6",
            "in_repair": "#f59e0b",
            "retired": "#6b7280"
        }.get(device["status"], "#6b7280")

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
if st.session_state.role == "admin":
    st.page_link("pages/users.py", label="Users", icon="🙎‍♂️")
else:
    st.markdown("### 🙎‍♂️ Users")

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

st.divider()

# ───── Recent logs ───────────────────────────────────────────
# ── Stat / if admin ───────────────────────────
if st.session_state.role == "admin":
    st.page_link("pages/logs.py", label="Logs", icon="🕰️")
else:
    st.markdown("###  Logs 🕰️")

logs = supabase.table("activity_logs") \
    .select("*, equipments(name), users(username)") \
    .order("created_at", desc=True) \
    .limit(20) \
    .execute().data

with st.container(border=True):
    if not logs:
        st.caption("No activity yet")
    else:
        for log in logs:
            equipment   = log["equipments"]["name"] if log["equipments"] else "—"
            username    = log["users"]["username"]  if log["users"]      else "—"
            log_date    = log["created_at"][:16].replace("T", " ")
            action      = log["action"]
            details     = log["details"] or {}
            details_str = "  ·  ".join(f"{k} : {v}" for k, v in details.items())

            st.caption(f"{log_date}  ·  {username}  ·  {action}  ·  {equipment}  {'·  ' + details_str if details_str else ''}")