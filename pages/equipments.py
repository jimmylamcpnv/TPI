import streamlit as st
import csv
import io
from datetime import date
from dateutil.relativedelta import relativedelta
from utils.auth import require_role
from utils.supabase.db_equipements import *
from pages.ocr import *

# ── Session ───────────────────────────────────────────────────
require_role(["admin", "standard"])

if "filtred_equipments" not in st.session_state:
    st.session_state["filtred_equipments"] = global_search(None)

# ── functions ─────────────────────────────────────────────────────
def generate_csv(equipments):
    # return empty if no datas
    if not equipments:
        return ""
    
    # create a text file in ram
    output = io.StringIO()

    # use the first item's keys as column headers (id, name, brand, ...)
    writer = csv.DictWriter(output, fieldnames=equipments[0].keys())
    writer.writeheader()          # write the header row
    writer.writerows(equipments)  # write all data rows at once
    
    # return the full CSV content as a string
    return output.getvalue()


def get_warranty_remaining(device):
    try:
        expiry = date.fromisoformat(str(device["purchase_date"])) + relativedelta(months=int(device["warranty_months"]))
        return (expiry - date.today()).days
    except:
        return None

# ── Dialogs ───────────────────────────────────────────────────
@st.dialog("Add device manually")
def add_device_manually():
    device_name      = st.text_input("Device name*")
    brand            = st.text_input("Brand*")
    model            = st.text_input("Model*")
    serial_number    = st.text_input("Serial number*")
    type             = st.multiselect("type", ['laptop', 'desktop', 'server', 'other'], max_selections=1, accept_new_options=False)
    status           = st.multiselect("Status", ['active', 'in_stock', 'in_repair', 'retired'], max_selections=1, accept_new_options=False)
    assigned_user_id = st.text_input("Assigned user (username)")
    purchase_date    = st.date_input("Purchase date")
    warranty_months  = st.text_input("Warranty period")
    supplier         = st.text_input("Supplier")

    with st.container(horizontal_alignment="right"):
        if st.button(label="Submit"):
            errors = []
            try:
                # get user id from username
                resolved_user_id = get_user_info(assigned_user_id)[0] if assigned_user_id else None
                
                create_equipment(
                    device_name,
                    brand,
                    model,
                    serial_number,
                    type[0],
                    status[0],
                    resolved_user_id["id"] if resolved_user_id else None,
                    purchase_date.isoformat() if purchase_date else None,
                    warranty_months or None,
                    supplier or None,
                )
                st.success(f"{device_name} has been added to supabase !")

            except Exception as error:
                # duplicate serial number
                if "duplicate key" in str(error) or "23505" in str(error):
                    st.error(f"Serial number already exists in the database")
                else:
                    st.error(str(error))

@st.dialog("Edit device datas")
def update_equipment(device):
    with st.container(border=True):
        new_device_name      = st.text_input("Device name*",             value=device["name"])
        new_brand            = st.text_input("Brand*",                   value=device["brand"])
        new_model            = st.text_input("Model*",                   value=device["model"])
        new_serial_number    = st.text_input("Serial number*",           value=device["serial_number"])
        new_type             = st.multiselect("Type",   ['laptop', 'desktop', 'server', 'other'],       default=device["type"],   max_selections=1, accept_new_options=False)
        new_status           = st.multiselect("Status", ['active', 'in_stock', 'in_repair', 'retired'], default=device["status"], max_selections=1, accept_new_options=False)
        new_assigned_user_id = st.text_input("Assigned user (username)", value=device["assigned_user_id"])
        new_purchase_date    = st.date_input("Purchase date",            value=device["purchase_date"])
        new_warranty_months  = st.text_input("Warranty period",          value=device["warranty_months"])
        new_supplier         = st.text_input("Supplier",                 value=device["supplier"])

    with st.container(border=False, horizontal_alignment="right"):
        if st.button("Save"):
            errors = []
            try:
                # get user id from username
                resolved_user_id = get_user_info(new_assigned_user_id)[0] if new_assigned_user_id else None
                
                update_equipments(
                    new_device_name,
                    new_brand,
                    new_model,
                    new_serial_number,
                    new_type,
                    new_status,
                    resolved_user_id["id"] or None,
                    new_purchase_date.isoformat() if new_purchase_date else None,
                    new_warranty_months,
                    new_supplier        or None,
                    device["serial_number"],
                )
                st.success(f"{new_device_name} has been updated successfully")

            except ValueError as error:
                errors.append(str(error))
                st.error(errors)

@st.dialog("Show device infos")
def show_device_info(device_name, brand, model, serial_number, type,
                     status, assigned_user_id, purchase_date, warranty_months, supplier, device_id):

    status_color = {
        "active"   : "green",
        "in_stock" : "blue",
        "retired"  : "gray",
        "in_repair": "orange"
    }.get(status, "gray")

    # ── Header : nom + serial number + badge status
    col_icon, col_name, col_badge = st.columns([0.7, 6, 2], vertical_alignment="center")
    with col_icon:  st.markdown("💻")
    with col_name:
        st.markdown(f"**{device_name}**")
        st.caption(f"S/N : '{serial_number}'")
    with col_badge: st.badge(status, color=status_color)

    st.divider()

    # ── Infos
    col1, col2 = st.columns(2)
    with col1:
        st.caption("BRAND");         st.markdown(f"**{brand}**")
        st.caption("TYPE");          st.markdown(f"**{type}**")
        st.caption("PURCHASE DATE"); st.markdown(f"**{purchase_date}**")

    with col2:
        st.caption("MODEL"); st.markdown(f"**{model}**")
        st.caption("ASSIGNED USER")
        # get user datas
        user_data = get_username_from_id(assigned_user_id)
        username  = user_data[0]["username"] if user_data else "—"
        st.markdown(f"**{username}**")
        st.caption("WARRANTY"); st.markdown(f"**{warranty_months} months**")
        st.caption("SUPPLIER"); st.markdown(f"**{supplier}**")

    # ── Buttons
    with st.container(horizontal=True):
        # delete
        with st.container(horizontal_alignment="left"):
            if st.button("Delete", type="primary"):
                errors = []
                try:
                    delete_equipment(serial_number)
                    st.success(f"{device_name} has been deleted")
                except ValueError as error:
                    errors.append(str(error))
                    st.error(errors)

        # edit
        with st.container(horizontal_alignment="right"):
            if st.button("Edit", type="secondary"):
                st.session_state["edit_device_target"] = device
                st.rerun()

    st.divider()

    # ── Logs
    with st.container():
        st.subheader("Logs")

        logs = supabase.table("activity_logs") \
            .select("*, users(username)") \
            .or_(f"equipment_id.eq.{device_id},details->>equipment_id.eq.{device_id}") \
            .order("created_at", desc=True) \
            .limit(10) \
            .execute().data

        if not logs:
            st.caption("nothing here")

        for log in logs:
            user   = log["users"]["username"] if log["users"] else "—"
            date   = log["created_at"][:16].replace("T", " ")
            action = log["action"]
            st.caption(f"{date}  ·  **{user}**  ·  {action}")

# ── Post-dialog session checks ────────────────────────────────
# store device's data of edited device, not the logged one
if "edit_device_target" in st.session_state:
    device_to_edit = st.session_state.pop("edit_device_target")
    update_equipment(device_to_edit)
    

# ── Header ────────────────────────────────────────────────────
col_title, scan_button, add_device = st.columns([8, 2, 2], vertical_alignment="center")

with col_title:
    st.markdown("<p style='font-size:2rem; margin:0; font-weight:bold'>🖥️ Equipments</p>", unsafe_allow_html=True)
    st.markdown(f"<small>Total devices : {len(global_search(None))}</small>", unsafe_allow_html=True)

with scan_button:
    if st.button("Scan", icon="📷", use_container_width=True):
        ocr()

with add_device:
    if st.button("Add device", type="secondary", width=100):
        add_device_manually()

# ── Filters ───────────────────────────────────────────────────
with st.container(border=True, vertical_alignment="center", horizontal=True):

    search_option = st.text_input("Search", key="filter_search")

    # initialize datas
    all_equipments     = global_search(search_option)
    filtred_equipments = all_equipments

    # type filter
    type_choice = st.selectbox("Type", ["All", "laptop", "desktop", "server", "other"], accept_new_options=False, key="filter_type")
    if type_choice != "All":
        filtred_equipments = [device for device in filtred_equipments if device["type"] == type_choice]

    # status filter
    status_choice = st.selectbox("Status", ["All", "active", "in_stock", "in_repair", "retired"], accept_new_options=False, key="filter_status")
    if status_choice != "All":
        filtred_equipments = [device for device in filtred_equipments if device["status"] == status_choice]

    # warranty sort by date
    warranty_sort = st.selectbox("Warranty", ["None", "↑ Expiring soon", "↓ Expiring late"], accept_new_options=False, key="filter_warranty")
    if warranty_sort != "None":
        filtred_equipments = sorted(
            filtred_equipments,
            key=lambda d: get_warranty_remaining(d) or (float("inf") if warranty_sort == "↑ Expiring soon" else float("-inf")),
            reverse=(warranty_sort == "↓ Expiring late")
        )

    # function to set all filters to default
    def reset_filters():
        st.session_state["filter_search"]   = ""
        st.session_state["filter_type"]     = "All"
        st.session_state["filter_status"]   = "All"
        st.session_state["filter_warranty"] = "None"

    # reset options
    if st.button(label="Reset", icon="🔄️", on_click=reset_filters):
        pass

# ── Results bar + CSV export ──────────────────────────────────
with st.container(vertical_alignment="center", horizontal=True):
    with st.container(horizontal=True, horizontal_alignment="left"):
        st.write(f"Result number : {len(filtred_equipments)}")
        st.badge(f"Type : {type_choice}")
        st.badge(f"Status : {status_choice}")

    with st.container(horizontal_alignment="right"):
        st.download_button("CSV", data=generate_csv(filtred_equipments),
                           file_name="equipments_export.csv", mime="text/csv", icon="📥")

st.session_state["filtred_equipments"] = filtred_equipments

# ── Display equipments ────────────────────────────────────────
for device in filtred_equipments:
    status_color = {
        "active"   : "#22c55e",
        "in_stock" : "#3b82f6",
        "in_repair": "#f59e0b",
        "retired"  : "#6b7280"
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
            # status badge
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

            # expiring days
            days = get_warranty_remaining(device)

            if days is None:    label, color = "No warranty",            "#6b7280"
            elif days < 0:      label, color = f"Expired {abs(days)}d",  "#ef4444"
            elif days <= 30:    label, color = f"⚠ {days}d left",        "#f59e0b"
            else:               label, color = f"{days}d left",           "#22c55e"

            st.markdown(f"""
                <span style="color:{color}; font-size:0.72rem;">🛡 {label}</span>
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
                    device["supplier"],
                    device["id"]
                )
