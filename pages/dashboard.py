import streamlit as st
from utils.supabase import *
import plotly.express as px
from utils.auth import require_role
import pandas as pd

# ── Guard ──────────────────────────────────────────
require_role(["admin", "standard"])

# ── Data ──────────────────────────────────────────────
all_equipments = get_all_equipements()

# transform into a structure table
df = pd.DataFrame(all_equipments)
all_users = get_all_users()

# ───── Equipements
st.page_link("pages/equipments.py", label="Equipments", icon="🖥️")
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

col1, col2 = st.columns(2, border=True)
# garanties (liste de ceux qui vont bientot exiprer)

# Tableau des dernières actions (logs) avec type d'action, utilisateur, date/heure

st.divider()

# ── Export ────────────────────────────────────────────
st.subheader("Export")
# Bouton export CSV — grisé pour standard (export en fonction des filtres)