from utils.supabase.db_connexion import supabase
import bcrypt

# Users
"""
.eq() = where
"""
# ── CREATE ────────────────────────────────────────
# create a user (username, password, role)
def create_user(username, password, role):
    supabase.table("users").insert({
        "username": username,
        "password_hash": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": role
    }).execute()

# ── READ ──────────────────────────────────────────
# get all info abount a user with the username
def get_user_info(username):
    if not username:
        return supabase.table("users").select("*").execute().data
    
    return supabase.table("users").select("*").ilike("username", f"%{username}%").execute().data

# ── UPDATE ────────────────────────────────────────
# update user datas
def update_user(username, role):
    supabase.table("users").update({
        "username"  : username,
        "role"      : role
    }
    )

# modifier le mdp du user via le id
def update_password(username, new_password):
    user = get_user_info(username)
    id = user[0]["id"]
    supabase.table("users").update({
        "password_hash": bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    }).eq("id", id).execute()

# ── DELETE ────────────────────────────────────────
# supprimer le user via le id
def delete_user(username):
    user = get_user_info(username)
    id = user[0]["id"]
    supabase.table("users").delete().eq("id", id).execute()