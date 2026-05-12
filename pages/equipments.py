import streamlit as st
from utils.auth import require_role
from utils.supabase.db_equipements import *
from pages.ocr import *
import csv
import io
"""
- delete
- ameliorer ocr
- update datas des equipements
- faire en sorte de reset les filtres
- trier par date de garantie
- add device (liste coulissantes, pré choix)
"""
# ── Session ──────────────────────────────────────────
require_role(["admin", "standard"])
if "filtred_equipments" not in st.session_state:
    st.session_state["filtred_equipments"] = global_search(None)

# ── Functions ──────────────────────────────────────────
# csv
def generate_csv(equipments):
    # return empty if no datas
    if not equipments:
        return ""
    
    # create a text file in ram
    output = io.StringIO()

    # use the first item's keys as column headers (id, name, brand, ...)
    writer = csv.DictWriter(output, fieldnames=equipments[0].keys())

      # write the header row
    writer.writeheader()

    # write all data rows at once
    writer.writerows(equipments)
    
    # return the full CSV content as a string
    return output.getvalue()

# add manually
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

# show device infos
@st.dialog("Show device infos")
def show_device_info(device_name, brand, model, serial_number, type,
                     status, assigned_user_id, purchase_date, warranty_months, supplier):

    status_color = {"active"        : "green",
                    "in_stock"      : "blue",
                    "retired"       : "gray",
                    "in_repair"     : "orange"}.get(status, "gray")

    # ── Header : nom + serial number + badge status
    col_icon, col_name, col_badge = st.columns([0.7, 6, 2], vertical_alignment="center")
    with col_icon:
        st.markdown("💻")
    with col_name:
        st.markdown(f"**{device_name}**")
        st.caption(f"S/N : '{serial_number}'")
    with col_badge:
        st.badge(status, color=status_color)

    st.divider()

    # ── Infos en grille 2 colonnes
    col1, col2 = st.columns(2)
    with col1:
        st.caption("BRAND")
        st.markdown(f"**{brand}**")
        st.caption("TYPE")
        st.markdown(f"**{type}**")
        st.caption("PURCHASE DATE")
        st.markdown(f"**{purchase_date}**")

    with col2:
        st.caption("MODEL")
        st.markdown(f"**{model}**")
        st.caption("ASSIGNED USER")
        st.markdown(f"**{assigned_user_id or '—'}**")
        st.caption("WARRANTY")
        st.markdown(f"**{warranty_months} months**")

    st.caption("SUPPLIER")
    st.markdown(f"**{supplier}**")

    with st.container(horizontal=True):
        with st.container(horizontal_alignment="left"):
            if st.button("Delete", type="primary"):
                errors = []
                try:
                    delete_equipment(serial_number)
                    st.success(f"{device_name} has been deleted")
                
                except ValueError as error:
                    errors.append(str(error))
                    st.error(errors)

        with st.container(horizontal_alignment="right"):
            if st.button("Edit", type="secondary"):
                pass

# ── Header / Buttons ──────────────────────────────────────────
# create 4 columns
col_title, scan_button, add_device = st.columns([8, 2, 2], vertical_alignment="center")

# title "equipments"
with col_title:
    st.markdown("<p style='font-size:2rem; margin:0; font-weight:bold'>🖥️ Equipments</p>", unsafe_allow_html=True)
    st.markdown(f"<small>Total devices : {len(global_search(None))}</small>", unsafe_allow_html=True)

# button scan ocr
with scan_button:
    if st.button("Scan", icon="📷", use_container_width=True):
        ocr()

# button add device manually
with add_device:
    if st.button("Add device", type="secondary", width=100):
        add_device_manually()

# ── Search / Filters ──────────────────────────────────────────
with st.container(border=True, vertical_alignment="center", horizontal=True):
    
    # search_options is the selected options
    search_option = st.text_input("Search")

    # initialize datas
    all_equipments = global_search(search_option)
    filtred_equipments = all_equipments

    # ── Buttons ──────────── 
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
    if st.button(label="Reset", icon="🔄️"):
        filtred_equipments = [device for device in all_equipments]

# ── Display filter + CSV
with st.container(vertical_alignment="center", horizontal=True):
    with st.container(horizontal=True, horizontal_alignment="left"):
        st.write(f"Result number : {len(filtred_equipments)}")
        st.badge(f"Type : {type_choice}")
        st.badge(f"Status : {status_choice}")

    with st.container(horizontal_alignment="right"):
        st.download_button("CSV", data=generate_csv(filtred_equipments),
                        file_name="equipments_export.csv", mime="text/csv", icon="📥")

# ── CSV download
st.session_state["filtred_equipments"] = filtred_equipments

# ── Display equipments ──────────────────────────────────────────
for device in filtred_equipments:
    status_color = {
        "active": "#22c55e",
        "in_stock": "#3b82f6",
        "in_repair": "#f59e0b",
        "retired": "#6b7280"
    }.get(device["status"], "#6b7280")

    with st.container(border=True):
        col_info, col_status, col_btn = st.columns([6, 2, 1], vertical_alignment="center")

        with col_info:
            st.markdown(f"""
                <strong style="font-size:1rem;">{device["name"]}</strong>
                <span style="color:#888; font-size:0.8rem; margin-left:8px;">{device["brand"]} · {device["model"]}</span>
                <br>
                <span style="color:#aaa; font-size:0.75rem;">SN: {device["serial_number"]} · {device["type"]}</span>
            """, unsafe_allow_html=True)

        with col_status:
            st.markdown(f"""
                <span style="
                    background:{status_color}22;
                    color:{status_color};
                    border:1px solid {status_color};
                    border-radius:20px;
                    padding:2px 10px;
                    font-size:0.75rem;
                ">{device["status"]}</span>
            """, unsafe_allow_html=True)

        with col_btn:
            if st.button("→", key=f"device_{device['id']}"):
                show_device_info(
                    device["name"],
                    device["brand"],
                    device["model"],
                    device["serial_number"],
                    device["type"],
                    device["status"],
                    device["assigned_user_id"],
                    device["purchase_date"],
                    device["warranty_months"],
                    device["supplier"]
                )