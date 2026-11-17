"""
Backend Configuration for SchoolGPT - RSR Technologies
Supports both local SQLite and Cloud PostgreSQL (with pgvector on Render).
Supports dual AI providers: Google Gemini API and local Ollama.
"""

import os
import json
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from typing import Optional, Union, List, Any

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="allow", case_sensitive=False)

    APP_NAME: str = "SchoolGPT"
    ORG_NAME: str = "RSR Technologies"
    TAGLINE: str = "Smart. Reliable. Instant Answers."
    VERSION: str = "2.5.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "rsr-technologies-schoolgpt-super-secret-jwt-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database: Supports Render PostgreSQL (postgresql://) or SQLite fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./schoolgpt_backend.db")

    # AI Provider: 'gemini' or 'ollama'
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "qwen3:4b")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text-v2-moe")

    # RAG Settings
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chromadb")
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./data/documents")
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 60
    TOP_K_CHUNKS: int = 4
    SIMILARITY_THRESHOLD: float = 0.40

    # CORS: Dynamic property supporting strings, wildcards (*), and JSON arrays
    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = os.getenv("CORS_ORIGINS", "*").strip()
        if not raw or raw == "*":
            return ["*"]
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed]
            except Exception:
                pass
        return [i.strip() for i in raw.split(",") if i.strip()]

settings = Settings()
