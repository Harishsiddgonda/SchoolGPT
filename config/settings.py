"""
SchoolGPT - Configuration and Settings
RSR Technologies - Smart • Reliable • Instant Answers
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Organization & Branding
APP_NAME = os.getenv("APP_NAME", "SchoolGPT")
APP_TAGLINE = os.getenv("APP_TAGLINE", "Smart • Reliable • Instant Answers")
APP_ORG = os.getenv("APP_ORG", "RSR Technologies")
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Directories
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
CHROMA_PERSIST_DIR = BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/schoolgpt.db")
ASSETS_DIR = BASE_DIR / "assets"
DEMO_DOCS_DIR = BASE_DIR / "demo_documents"

# Ensure directories exist
for path in [DATA_DIR, UPLOAD_DIR, CHROMA_PERSIST_DIR, ASSETS_DIR, DEMO_DOCS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Ollama & LLM Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "qwen3:4b")
OLLAMA_FALLBACK_MODELS = [
    m.strip() for m in os.getenv("OLLAMA_FALLBACK_MODELS", "llama3.2:3b,mistral:7b,llama3:8b,gemma:7b").split(",")
]
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# Embeddings Configuration
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text-v2-moe")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
FALLBACK_EMBEDDINGS = os.getenv("FALLBACK_EMBEDDINGS", "true").lower() in ("true", "1", "yes")

# RAG & Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))

# Roles
ROLES = [
    "Super Admin",
    "School Administrator",
    "Principal",
    "Teacher",
    "Student",
    "Parent"
]

ADMIN_ROLES = ["Super Admin", "School Administrator"]
STAFF_ROLES = ["Super Admin", "School Administrator", "Principal", "Teacher"]

# Document Categories
DOCUMENT_CATEGORIES = [
    "School Policies",
    "Student Handbook",
    "Admission Guidelines",
    "Fee Structure",
    "Examination Timetable",
    "Academic Calendar",
    "School Circulars",
    "Parent Guidelines",
    "Teacher Guidelines",
    "Transport Policies",
    "Hostel Policies",
    "General Documents"
]

# Multilingual Languages
LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"}
}

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# Grounding Message when info is unavailable in uploaded documents
INSUFFICIENT_INFO_MESSAGE = (
    "I could not find reliable information about this question in the school's uploaded documents. "
    "Please contact the school administration."
)

INSUFFICIENT_INFO_TRANSLATIONS = {
    "en": INSUFFICIENT_INFO_MESSAGE,
    "kn": "ಶಾಲೆಯ ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ದಾಖಲೆಗಳಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಶಾಲಾ ಆಡಳಿತವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    "hi": "स्कूल के अपलोड किए गए दस्तावेज़ों में इस प्रश्न के बारे में विश्वसनीय जानकारी नहीं मिली। कृपया स्कूल प्रशासन से संपर्क करें।"
}

# Theme Colors (Matching Reference Image)
THEME_COLORS = {
    "navy_primary": "#0F172A",
    "navy_secondary": "#1E293B",
    "royal_blue": "#1D4ED8",
    "royal_blue_light": "#2563EB",
    "purple_gradient_start": "#7C3AED",
    "purple_gradient_end": "#4F46E5",
    "accent_gold": "#F59E0B",
    "accent_green": "#10B981",
    "card_bg": "#FFFFFF",
    "text_dark": "#0F172A",
    "text_muted": "#64748B",
    "border_light": "#E2E8F0"
}
