"""
SchoolGPT - Authentication Module
RSR Technologies
"""

import bcrypt
from typing import Optional, Dict, Any, Tuple
from database.models import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_last_login,
    update_user_password,
    log_activity
)

def hash_password(plain_password: str) -> str:
    """Hashes a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def authenticate_user(username_or_email: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Authenticates a user by username or email.
    Returns (user_dict, error_message).
    """
    cleaned = username_or_email.strip()
    user = get_user_by_username(cleaned) or get_user_by_email(cleaned.lower())

    if not user:
        return None, "Invalid username or password."

    if not user.get("is_active"):
        return None, "This account has been deactivated. Please contact your school administrator."

    if not verify_password(password, user["password_hash"]):
        return None, "Invalid username or password."

    # Update last login and audit log
    update_last_login(user["id"])
    log_activity(user["id"], "LOGIN", f"User {user['username']} logged in successfully")

    # Strip sensitive hash before returning session user
    user_data = dict(user)
    user_data.pop("password_hash", None)
    return user_data, ""

def register_user(
    username: str,
    email: str,
    full_name: str,
    role: str,
    password: str,
    creator_id: Optional[int] = None
) -> Tuple[bool, str]:
    """Registers a new user (usually by Administrator)."""
    username = username.strip()
    email = email.strip().lower()
    full_name = full_name.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if "@" not in email or "." not in email:
        return False, "Please provide a valid email address."

    if get_user_by_username(username):
        return False, f"Username '{username}' is already taken."
    if get_user_by_email(email):
        return False, f"Email '{email}' is already registered."

    hashed = hash_password(password)
    user_id = create_user(username, email, full_name, role, hashed)

    log_activity(creator_id, "USER_CREATED", f"Created user {username} with role {role}")
    return True, f"User '{username}' registered successfully."

def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
    """Allows a user to change their own password."""
    user = get_user_by_id(user_id)
    if not user:
        return False, "User not found."

    if not verify_password(old_password, user["password_hash"]):
        return False, "Current password is incorrect."

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    hashed = hash_password(new_password)
    update_user_password(user_id, hashed)
    log_activity(user_id, "PASSWORD_CHANGED", "User updated their password")
    return True, "Password updated successfully."

def reset_user_password_by_admin(admin_id: int, target_user_id: int, new_password: str) -> Tuple[bool, str]:
    """Allows an administrator to reset a user's password."""
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."
    hashed = hash_password(new_password)
    update_user_password(target_user_id, hashed)
    log_activity(admin_id, "ADMIN_PASSWORD_RESET", f"Admin reset password for user #{target_user_id}")
    return True, "Password reset successfully."
