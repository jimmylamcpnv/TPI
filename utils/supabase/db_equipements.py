from utils.supabase.db_connexion import supabase
from utils.supabase.db_users import *
from utils.logger import log_action

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
    result = supabase.table("equipments").insert({
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

    # log the creation
    new_id = result.data[0]["id"]
    log_action("create_equipment", new_id, {"serial_number": serial_number})

# ── UPDATE ────────────────────────────────────────
def update_equipments(device_name, brand, model, serial_number, type, status, assigned_user_id, purchase_date, warranty_months, supplier, original_serial_number):
    
    # get old data + id before update
    old = supabase.table("equipments").select("*").eq("serial_number", original_serial_number).execute().data
    equipment_id = old[0]["id"] if old else None

    # find what changed
    new_values = {
        "name":            device_name,
        "brand":           brand,
        "model":           model,
        "serial_number":   serial_number,
        "type":            type[0] if isinstance(type, list) else type,
        "status":          status[0] if isinstance(status, list) else status,
        "purchase_date":   str(purchase_date) if purchase_date else None,
        "warranty_months": warranty_months,
        "supplier":        supplier,
    }

    changes = {
        key: {"old": old[0][key], "new": val}
        for key, val in new_values.items()
        if str(old[0].get(key)) != str(val)
    }

    supabase.table("equipments").update({
        **new_values,
        "assigned_user_id": assigned_user_id,
    }).eq("serial_number", original_serial_number).execute()

    # log with all changes
    log_action("update_equipment", equipment_id=equipment_id, details=changes)

# ── DELETE ────────────────────────────────────────
def delete_equipment(serial_number):
    # result of the equipment sort by serial number
    result = supabase.table("equipments")\
        .select("id")\
        .eq("serial_number", serial_number)\
        .single()\
        .execute()
    
    equipment_id = result.data["id"]

    # logs
    log_action(
        equipment_id=equipment_id,
        action="delete_equipment",
        details={
            "serial_number": serial_number,
            "equipment_id": equipment_id
    }
    )

    # delete
    supabase.table("equipments")\
        .delete()\
        .eq("serial_number", serial_number)\
        .execute()