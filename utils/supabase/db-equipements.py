from utils.supabase import supabase
# .data
# .count
# .error

# Equipements
# ── READ ──────────────────────────────────────────
def get_all_equipements():
    return supabase.table("equipements").select("*").execute().data
# ── CREATE ────────────────────────────────────────
# ── UPDATE ────────────────────────────────────────
# ── DELETE ────────────────────────────────────────