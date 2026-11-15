"""
SchoolGPT - User Management Service
RSR Technologies
"""

from typing import List, Dict, Any, Tuple
from database.models import (
    get_all_users,
    get_user_by_id,
    update_user_status,
    update_user_role,
    delete_user,
    log_activity
)
from auth.authentication import register_user, reset_user_password_by_admin

class UserService:
    def list_users(self) -> List[Dict[str, Any]]:
        return get_all_users()

    def toggle_user_status(self, user_id: int, current_status: bool, admin_id: int) -> Tuple[bool, str]:
        new_status = not current_status
        update_user_status(user_id, new_status)
        action = "activated" if new_status else "deactivated"
        log_activity(admin_id, "USER_STATUS_CHANGE", f"User #{user_id} {action}")
        return True, f"User successfully {action}."

    def change_role(self, user_id: int, new_role: str, admin_id: int) -> Tuple[bool, str]:
        update_user_role(user_id, new_role)
        log_activity(admin_id, "USER_ROLE_CHANGE", f"User #{user_id} role updated to {new_role}")
        return True, f"Role updated to {new_role}."

    def remove_user(self, user_id: int, admin_id: int) -> Tuple[bool, str]:
        if user_id == admin_id:
            return False, "You cannot delete your own administrator account."
        delete_user(user_id)
        log_activity(admin_id, "USER_DELETED", f"Deleted user #{user_id}")
        return True, "User deleted successfully."

user_service = UserService()
