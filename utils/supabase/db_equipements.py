from utils.supabase.db_connexion import supabase  # ✅
from utils.supabase.db_users import *
# Equipements
# ── READ ──────────────────────────────────────────
# all equipments data in a list
def get_all_equipements():
    return supabase.table("equipments").select("*").execute().data

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
def delete_equipment(username):
    user = get_user_info(username)
    id = user[0]["id"]
    supabase.table("users").delete().eq("id", id).execute()