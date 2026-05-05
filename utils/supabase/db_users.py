from utils.supabase.db_connexion import supabase
import bcrypt

# Users
"""
.eq() = where
"""
# ── CREATE ────────────────────────────────────────
# creer un user (username, password, role)
def create_user(username, password, role):
    supabase.table("users").insert({
        "username": username,
        "password_hash": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": role
    }).execute()

# ── READ ──────────────────────────────────────────
# avoir le user depuis le username pour le login
def get_user_info(username):
    return supabase.table("users").select("*").eq("username", username).execute().data

# avoir tt les users pour afficher la liste des users dans la page users
def get_all_users():
    return supabase.table("users").select("*").execute().data

# ── UPDATE ────────────────────────────────────────
# modifier user (username, role)
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