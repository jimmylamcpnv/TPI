import streamlit as st
from utils.auth import require_role
from utils.supabase.db_connexion import supabase

# ── Guard ─────────────────────────────────────────
require_role(["admin"])

# ── Fetch logs ────────────────────────────────────
result = supabase.table("activity_logs") \
    .select("*, users(username), equipments!activity_logs_equipment_id_fkey(serial_number, name)") \
    .order("created_at", desc=True) \
    .limit(100) \
    .execute()

# ── Header ────────────────────────────────────────
st.markdown("<p style='font-size:2rem; font-weight:bold'>📋 Logs</p>", unsafe_allow_html=True)
st.markdown(f"<small>{len(result.data)} last actions</small>", unsafe_allow_html=True)
st.divider()

# ── Action styles ─────────────────────────────────
action_color = {
    "login_success"    : "#22c55e",
    "login_failed"     : "#ef4444",
    "create_equipment" : "#3b82f6",
    "update_equipment" : "#f59e0b",
    "delete_equipment" : "#ef4444",
    "assign_equipment" : "#a855f7",
    "ocr_scan"         : "#06b6d4",
    "create_user"      : "#3b82f6",
    "update_user"      : "#f59e0b",
    "update_password"  : "#f59e0b",
    "delete_user"      : "#ef4444",
}

action_icon = {
    "login_success"    : "✅",
    "login_failed"     : "❌",
    "create_equipment" : "➕",
    "update_equipment" : "✏️",
    "delete_equipment" : "🗑️",
    "assign_equipment" : "👤",
    "ocr_scan"         : "📷",
    "create_user"      : "👤",
    "update_user"      : "✏️",
    "update_password"  : "🔑",
    "delete_user"      : "🗑️",
}

# ── Display ───────────────────────────────────────
for log in result.data:
    user      = log["users"]["username"]           if log["users"]      else "—"
    equipment = log["equipments"]["name"]           if log["equipments"] else None
    sn        = log["equipments"]["serial_number"]  if log["equipments"] else None
    details   = log["details"] or {}
    action    = log["action"]
    color     = action_color.get(action, "#6b7280")
    icon      = action_icon.get(action, "•")
    date      = log["created_at"][:16].replace("T", " ")

    # build details string
    details_str = "  ·  ".join(f"{k} : {v}" for k, v in details.items()) if details else ""

    equipment_str = f"📦 {equipment} · {sn}" if equipment else ""

    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 10px 14px;
            border-left: 3px solid {color};
            margin-bottom: 6px;
            border-radius: 0 6px 6px 0;
            background: {color}0d;
        ">
            <span style="font-size:1.1rem">{icon}</span>
            <span style="color:#aaa; font-size:0.75rem; min-width:110px">{date}</span>
            <span style="
                background:{color}22; color:{color};
                border:1px solid {color}; border-radius:20px;
                padding:2px 10px; font-size:0.72rem; white-space:nowrap;
            ">{action}</span>
            <span style="font-weight:600; font-size:0.85rem; min-width:80px">{user}</span>
            <span style="color:#888; font-size:0.8rem">{equipment_str}</span>
            <span style="color:#666; font-size:0.75rem; margin-left:auto">{details_str}</span>
        </div>
    """, unsafe_allow_html=True)