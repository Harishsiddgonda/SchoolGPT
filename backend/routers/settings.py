"""
System Settings Router for SchoolGPT
Allows administrators to inspect and configure AI Providers (Gemini / Ollama), models, and vector database status.
RSR Technologies
"""

import os
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User, DocumentChunk
from backend.auth.dependencies import get_current_user, require_min_role
from backend.config import settings
from backend.rag.gemini_client import gemini_client
from backend.rag.ollama_client import ollama_client

router = APIRouter(prefix="/settings", tags=["System Settings"])

class SettingsUpdate(BaseModel):
    ai_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    ollama_model: Optional[str] = None
    ollama_url: Optional[str] = None

@router.get("")
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_chunks = db.query(DocumentChunk).count()
    return {
        "app_name": settings.APP_NAME,
        "org_name": settings.ORG_NAME,
        "version": settings.VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "gemini_configured": gemini_client.is_available(),
        "gemini_model": settings.GEMINI_MODEL,
        "ollama_connected": ollama_client.is_available(),
        "ollama_model": settings.OLLAMA_LLM_MODEL,
        "ollama_url": settings.OLLAMA_BASE_URL,
        "embedding_model": settings.OLLAMA_EMBED_MODEL,
        "vector_db": "ChromaDB + PostgreSQL pgvector",
        "total_vectors": total_chunks
    }

@router.post("")
def update_settings(
    req: SettingsUpdate,
    current_user: User = Depends(require_min_role("School Admin")),
    db: Session = Depends(get_db)
):
    if req.ai_provider:
        settings.AI_PROVIDER = req.ai_provider
    if req.gemini_model:
        settings.GEMINI_MODEL = req.gemini_model
    if req.gemini_api_key:
        settings.GEMINI_API_KEY = req.gemini_api_key
        gemini_client.api_key = req.gemini_api_key
        gemini_client._init_client()
    if req.ollama_model:
        settings.OLLAMA_LLM_MODEL = req.ollama_model
        ollama_client.model_name = req.ollama_model
    if req.ollama_url:
        settings.OLLAMA_BASE_URL = req.ollama_url
        ollama_client.base_url = req.ollama_url.rstrip("/")

    return {"message": "Settings updated successfully", "current_provider": settings.AI_PROVIDER}
