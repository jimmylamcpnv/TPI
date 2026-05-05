import streamlit as st
from utils.auth import require_role
from utils.supabase.db_equipements import *

# ── Session ──────────────────────────────────────────
require_role(["admin", "standard"])

# ── Data ──────────────────────────────────────────
all_equipments = get_all_equipements()
filtred_equipments = all_equipments

# ── Functions ──────────────────────────────────────────
@st.dialog("Add device manually")
def add_device_manually():
    device_name = st.text_input("Device name*")
    brand = st.text_input("Brand*")
    model = st.text_input("Model*")
    serial_number = st.text_input("Serial number*")
    type = st.text_input("type* ('laptop', 'desktop', 'server', 'other')")
    status = st.text_input("Status* ('active', 'in_stock', 'in_repair', 'retired')")
    assigned_user_id = st.text_input("Assigned user (username)")
    purchase_date = st.text_input("Purchase date")
    warranty_months = st.text_input("Warranty period")
    supplier = st.text_input("Supplier")

    if st.button(label="Submit"):
        errors = []
        try:
            create_equipment(
                device_name, 
                brand,
                model,
                serial_number,
                type, status,
                assigned_user_id or None,
                purchase_date or None,
                warranty_months or None,
                supplier or None,
                )
            st.success(f"{device_name} has been added to supabase !")

        except ValueError as error:
            errors.append(str(error))
            st.error(errors)
        # mettre des logs de l'erreur

# ── Header / Buttons ──────────────────────────────────────────

col_title, col1, col2, col3 = st.columns([5.5, 1.5, 1.5, 1.8], vertical_alignment="center")

with col_title:
    st.markdown("<p style='font-size:2rem; margin:0; font-weight:bold'>🖥️ Equipments</p>", unsafe_allow_html=True)
    st.markdown("<small>hello world</small>", unsafe_allow_html=True)

with col1:
    if st.button("CSV", icon="📥", use_container_width=True):
        pass

with col2:
    st.button("Scan", icon="📷", use_container_width=True)

with col3:
    if st.button("Add device", type="primary", width=100):
        add_device_manually()

# ── Search / Filters ──────────────────────────────────────────
with st.container(border=True, vertical_alignment="center", horizontal=True):
        
    # search_options is the selected options
    search_options = st.multiselect(
        "Search",
        ["Test", "Test2"],
        accept_new_options=True,
    )
    """
    
    """
    # type filter
    type_choice = st.selectbox("Type", ["All", "laptop", "desktop", "server", "other"], accept_new_options=False)
    if type_choice != "All":
        filtred_equipments = [device for device in filtred_equipments if device["type"] == type_choice
                              ]
    
    # status filter
    status_choice = st.selectbox("Status", ["All", "active", "in_stock", "in_repair", "retired"], accept_new_options=False)
    if status_choice != "All":
        filtred_equipments = [device for device in filtred_equipments if device["status"] == status_choice]
    
    # warranty sort by date
    warranty_sort = st.selectbox("Warranty", ["None", "↑ Expiring soon", "↓ Expiring late"], accept_new_options=False)
    st.button(label="Reset", icon="🔄️")

# ── Display filter
with st.container(vertical_alignment="center", horizontal=True):
    st.badge(f"Type : {type_choice}")
    st.badge(f"Status : {status_choice}")

# ── Display equipments ──────────────────────────────────────────

with st.container(border=False, height=1200):
    for device in filtred_equipments:
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