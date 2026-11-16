"""
Health Check Router for SchoolGPT API v1
RSR Technologies
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database.db import get_db
from backend.config import settings
from backend.rag.gemini_client import gemini_client
from backend.rag.ollama_client import ollama_client

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
def api_v1_health(db: Session = Depends(get_db)):
    # Check DB
    db_healthy = False
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "SchoolGPT Enterprise API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_healthy else "disconnected",
        "ai_provider": settings.AI_PROVIDER,
        "gemini_active": gemini_client.is_available(),
        "ollama_active": ollama_client.is_available()
    }
