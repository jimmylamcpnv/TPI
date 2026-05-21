import re
import random
import numpy as np
import streamlit as st
from PIL import Image
from utils.logger import log_action
from utils.supabase.db_equipements import *
from doctr.models import ocr_predictor

#########################################
############## Photo / OCR ##############
#########################################

# load the model into the cache to avoid loading for every click
@st.cache_resource
def load_model():
    return ocr_predictor(
        pretrained=True,
        assume_straight_pages=False,
        straighten_pages=True,
        detect_orientation=True
    )

# ── fake dell api ──────────────────────────────────────────────────────────────
# simulates what a real dell api would return given a service tag
def fake_dell_api(service_tag):
    # seed with the service tag so the same tag always returns the same data
    random.seed(service_tag)

    models = [
        ("Latitude", "5540"),
        ("Latitude", "7440"),
        ("OptiPlex", "7010"),
        ("OptiPlex", "3000"),
        ("Precision", "3580"),
        ("XPS", "15 9530"),
    ]

    suppliers = ["Dell Direct", "Interdell SA", "Microspot", "Digitec"]

    name, model_number = random.choice(models)
    warranty_months    = random.choice([12, 24, 36, 48])
    purchase_year      = random.randint(2020, 2024)
    purchase_month     = random.randint(1, 12)
    purchase_day       = random.randint(1, 28)

    return {
        "name":             f"Dell {name} {model_number}",
        "brand":            "Dell",
        "model":            f"{name} {model_number}",
        "serial_number":    service_tag,
        "type":             "laptop" if name in ("Latitude", "XPS", "Precision") else "desktop",
        "status":           "active",
        "purchase_date":    f"{purchase_year}-{purchase_month:02d}-{purchase_day:02d}",
        "warranty_months":  warranty_months,
        "supplier":         random.choice(suppliers),
        "assigned_user_id": None,
    }

# ── ocr dialog ─────────────────────────────────────────────────────────────────
@st.dialog("OCR dialog")
def ocr():
    file = st.camera_input("take a picture") or st.file_uploader("upload a file here")

    # dell service tag pattern: 7 uppercase alphanumeric characters
    pattern = re.compile(r"[A-Z0-9]{7}")

    if file is not None:
        img    = Image.open(file).convert("RGB")
        img_np = np.array(img)

        model  = load_model()
        result = model([img_np])

        text        = result.render()
        glued_text  = "".join(text.split())

        matches    = pattern.findall(glued_text)
        valid_tags = [m for m in matches if re.search(r"[A-Z]", m)]

        st.image(img_np)

        # ── step 1 : confirm / correct the detected service tag ───────────────
        st.subheader("Service tag")

        detected = valid_tags[0] if valid_tags else ""

        if detected:
            st.success(f"Detected : {detected}")
        else:
            st.warning("No service tag detected — enter it manually")

        # let the user correct or enter the service tag manually
        service_tag = st.text_input(
            "Confirm or correct the service tag",
            value=detected,
            max_chars=7,
            placeholder="ex: ABC1234"
        ).strip().upper()

        if not service_tag:
            st.stop()

        # ── step 2 : fetch simulated dell data ────────────────────────────────
        st.subheader("Device data")
        st.caption("data returned by the dell api (simulated)")

        data = fake_dell_api(service_tag)

        # display each field as an editable input so the user can fix anything
        col1, col2 = st.columns(2)

        with col1:
            data["name"]            = st.text_input("Name",           value=data["name"])
            data["brand"]           = st.text_input("Brand",          value=data["brand"])
            data["model"]           = st.text_input("Model",          value=data["model"])
            data["serial_number"]   = st.text_input("Serial number",  value=data["serial_number"])

        with col2:
            data["type"]            = st.selectbox("Type",     ["laptop", "desktop", "server", "other"], index=["laptop", "desktop", "server", "other"].index(data["type"]))
            data["status"]          = st.selectbox("Status",   ["active", "in_stock", "in_repair", "retired"], index=0)
            data["purchase_date"]   = st.text_input("Purchase date",      value=data["purchase_date"])
            data["warranty_months"] = st.number_input("Warranty (months)", value=data["warranty_months"], min_value=0, step=1)

        data["supplier"] = st.text_input("Supplier", value=data["supplier"])

        # ── step 3 : confirm and return the data ─────────────────────────────
        with st.container(horizontal_alignment="right"):
            if st.button("Confirm and use this data", type="primary"):
                try:
                    create_equipment(
                        device_name      = data["name"],
                        brand            = data["brand"],
                        model            = data["model"],
                        serial_number    = data["serial_number"],
                        type             = data["type"],
                        status           = data["status"],
                        assigned_user_id = data["assigned_user_id"],
                        purchase_date    = data["purchase_date"],
                        warranty_months  = data["warranty_months"],
                        supplier         = data["supplier"],
                    )

                    st.session_state["ocr_result"] = data

                    log_action("ocr_scan", details={
                        "detected":  detected,
                        "confirmed": service_tag,
                        "corrected": detected != service_tag,
                    })

                    st.success("Equipment saved successfully!")
                    st.rerun()

                except Exception as e:
                    error_msg = str(e)
                    if "23505" in error_msg or "duplicate key" in error_msg:
                        st.error(f"Serial number **{data['serial_number']}** already exists in the database.")
                    else:
                        st.error(f"Error saving equipment: {error_msg}")