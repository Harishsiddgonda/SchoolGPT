"""
API v1 Router Aggregator for SchoolGPT
Mounts all versioned REST endpoints under /api/v1/
RSR Technologies
"""

from fastapi import APIRouter
from backend.routers import auth, chat, documents, bookmarks, analytics, users, settings as settings_router
from backend.api.v1 import health, notifications

api_v1_router = APIRouter(prefix="/api/v1")

# Mount Routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router, prefix="", tags=["Authentication v1"])
api_v1_router.include_router(chat.router, prefix="", tags=["Chat & RAG v1"])
api_v1_router.include_router(documents.router, prefix="", tags=["Documents v1"])
api_v1_router.include_router(bookmarks.router, prefix="", tags=["Bookmarks v1"])
api_v1_router.include_router(analytics.router, prefix="", tags=["Analytics v1"])
api_v1_router.include_router(users.router, prefix="", tags=["Users v1"])
api_v1_router.include_router(settings_router.router, prefix="", tags=["Settings v1"])
api_v1_router.include_router(notifications.router)
