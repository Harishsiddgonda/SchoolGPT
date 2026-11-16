"""
SQLAlchemy Models for SchoolGPT
Re-exports from backend.models.models for unified model registry.
RSR Technologies
"""

from backend.models.models import (
    Base,
    Role,
    User,
    Document,
    DocumentPermission,
    DocumentChunk,
    Conversation,
    Message,
    QueryHistory,
    Bookmark,
    Feedback,
    Notification,
    ActivityLog,
    SchoolSetting
)

__all__ = [
    "Base",
    "Role",
    "User",
    "Document",
    "DocumentPermission",
    "DocumentChunk",
    "Conversation",
    "Message",
    "QueryHistory",
    "Bookmark",
    "Feedback",
    "Notification",
    "ActivityLog",
    "SchoolSetting"
]
