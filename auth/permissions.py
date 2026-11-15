"""
SchoolGPT - Permissions & Role-Based Access Control (RBAC)
RSR Technologies
"""

from typing import List, Dict, Any, Optional
from config.settings import ROLES, ADMIN_ROLES, STAFF_ROLES

# Role Permissions Matrix
ROLE_PERMISSIONS = {
    "Super Admin": {
        "can_view_dashboard": True,
        "can_chat": True,
        "can_view_kb": True,
        "can_upload_docs": True,
        "can_delete_docs": True,
        "can_reindex_docs": True,
        "can_view_analytics": True,
        "can_manage_users": True,
        "can_edit_settings": True,
        "can_export_data": True,
        "allowed_doc_visibility": ROLES,
    },
    "School Administrator": {
        "can_view_dashboard": True,
        "can_chat": True,
        "can_view_kb": True,
        "can_upload_docs": True,
        "can_delete_docs": True,
        "can_reindex_docs": True,
        "can_view_analytics": True,
        "can_manage_users": True,
        "can_edit_settings": True,
        "can_export_data": True,
        "allowed_doc_visibility": ROLES,
    },
    "Principal": {
        "can_view_dashboard": True,
        "can_chat": True,
        "can_view_kb": True,
        "can_upload_docs": True,
        "can_delete_docs": False,
        "can_reindex_docs": False,
        "can_view_analytics": True,
        "can_manage_users": False,
        "can_edit_settings": False,
        "can_export_data": True,
        "allowed_doc_visibility": ["Principal", "Teacher", "Student", "Parent"],
    },
    "Teacher": {
        "can_view_dashboard": True,
        "can_chat": True,
        "can_view_kb": True,
        "can_upload_docs": True,
        "can_delete_docs": False,
        "can_reindex_docs": False,
        "can_view_analytics": False,
        "can_manage_users": False,
        "can_edit_settings": False,
        "can_export_data": False,
        "allowed_doc_visibility": ["Teacher", "Student", "Parent"],
    },
    "Student": {
        "can_view_dashboard": False,
        "can_chat": True,
        "can_view_kb": True,
        "can_upload_docs": False,
        "can_delete_docs": False,
        "can_reindex_docs": False,
        "can_view_analytics": False,
        "can_manage_users": False,
        "can_edit_settings": False,
        "can_export_data": False,
        "allowed_doc_visibility": ["Student"],
    },
    "Parent": {
        "can_view_dashboard": False,
        "can_chat": True,
        "can_view_kb": True,
        "can_upload_docs": False,
        "can_delete_docs": False,
        "can_reindex_docs": False,
        "can_view_analytics": False,
        "can_manage_users": False,
        "can_edit_settings": False,
        "can_export_data": False,
        "allowed_doc_visibility": ["Parent"],
    }
}

def has_permission(user_role: str, permission_key: str) -> bool:
    """Checks if a user role has a specific capability."""
    perms = ROLE_PERMISSIONS.get(user_role, {})
    return perms.get(permission_key, False)

def can_access_document(user_role: str, document_allowed_roles: List[str]) -> bool:
    """
    CRITICAL SECURITY CHECK:
    Determines whether a user with `user_role` can view or retrieve
    content from a document whose allowed_roles is `document_allowed_roles`.
    """
    if user_role in ADMIN_ROLES:
        return True
    return user_role in document_allowed_roles

def filter_documents_for_role(documents: List[Dict[str, Any]], user_role: str) -> List[Dict[str, Any]]:
    """Filters a list of document dicts to only those allowed for user_role."""
    if user_role in ADMIN_ROLES:
        return documents
    return [d for d in documents if can_access_document(user_role, d.get("allowed_roles_list", []))]

def get_role_badge_color(role: str) -> str:
    """Returns CSS color style for role tags."""
    mapping = {
        "Super Admin": "#7C3AED",
        "School Administrator": "#1D4ED8",
        "Principal": "#0284C7",
        "Teacher": "#059669",
        "Student": "#D97706",
        "Parent": "#DC2626"
    }
    return mapping.get(role, "#4B5563")
