from utils.supabase.db_connexion import supabase
from utils.logger import log_action
import bcrypt

# Users
# ── CREATE ────────────────────────────────────────
# create a user (username, password, role)
def create_user(username, password, role):
    supabase.table("users").insert({
        "username":      username,
        "password_hash": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role":          role
    }).execute()

    # log the creation
    log_action("create_user", details={"username": username, "role": role})

# ── READ ──────────────────────────────────────────
# get all info about a user with the username
def get_user_info(username):
    if username:
        return supabase.table("users").select("*").ilike("username", f"%{username}%").execute().data
    else:
        return supabase.table("users").select("*").execute().data

def get_username_from_id(id):
    if id:
        return supabase.table("users").select("username").eq("id", id).execute().data
    else:
        return None

# ── UPDATE ────────────────────────────────────────
# update user datas
def update_user(actual_username, new_username, role):
    user = get_user_info(actual_username)

    if not user:
        raise ValueError(f"User '{actual_username}' not found")

    id = int(user[0]["id"])

    response = supabase.table("users").update({
        "username": new_username,
        "role":     role
    }).eq("id", id).execute()

    # log the update
    log_action("update_user", details={"old_username": actual_username, "new_username": new_username, "role": role})

    return response.data

# update the password via user id
def update_password(username, new_password):
    user = get_user_info(username)
    id   = user[0]["id"]

    supabase.table("users").update({
        "password_hash": bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    }).eq("id", id).execute()

    # log the password update
    log_action("update_password", details={"username": username})

# ── DELETE ────────────────────────────────────────
# delete user via id
def delete_user(username):
    user = get_user_info(username)
    id   = user[0]["id"]

    supabase.table("users").delete().eq("id", id).execute()

    # log the deletion
    log_action("delete_user", details={"username": username})