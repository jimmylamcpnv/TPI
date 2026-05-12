from utils.supabase.db_connexion import supabase  # ✅
from utils.supabase.db_users import *
# Equipements
# ── READ ──────────────────────────────────────────
def global_search(search_option):
    # if no result, display everything
    if not search_option:
        return supabase.table("equipments").select("*").execute().data
    
    return (
        supabase.table("equipments")
        .select("*")
        .or_(
            f"name.ilike.%{search_option}%,"
            f"brand.ilike.%{search_option}%,"
            f"model.ilike.%{search_option}%,"
            f"serial_number.ilike.%{search_option}%,"
            f"type.ilike.%{search_option}%,"
            f"status.ilike.%{search_option}%"
        )
        .execute()
        .data
    )

# ── CREATE ────────────────────────────────────────
def create_equipment(device_name, brand, model, serial_number, type, status, assigned_user_id, purchase_date, warranty_months, supplier):
    supabase.table("equipments").insert({
        "name":             device_name,
        "brand":            brand,
        "model":            model,
        "serial_number":    serial_number,
        "type":             type,
        "status":           status,
        "assigned_user_id": assigned_user_id,
        "purchase_date":    purchase_date,
        "warranty_months":  warranty_months,
        "supplier":         supplier
    }).execute()

# ── UPDATE ────────────────────────────────────────
def update_equipments(id, device_name, brand, model, serial_number, type, status, assigned_user_id, purchase_date, warranty_months, supplier):
    supabase.table("equipments").update({
        "name":             device_name,
        "brand":            brand,
        "model":            model,
        "serial_number":    serial_number,
        "type":             type,
        "status":           status,
        "assigned_user_id": assigned_user_id,
        "purchase_date":    purchase_date,
        "warranty_months":  warranty_months,
        "supplier":         supplier
    }).eq("id", id).execute()

# ── DELETE ────────────────────────────────────────
def delete_equipment(serial_number):
    supabase.table("equipments").delete().eq("serial_number", serial_number).execute()