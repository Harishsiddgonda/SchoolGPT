"""
SchoolGPT - Master FastAPI Application Entrypoint
Organization: RSR Technologies
Tagline: Smart. Reliable. Instant Answers.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.db import init_db, SessionLocal
from backend.database.models import User, Document, DocumentChunk
from backend.auth.security import get_password_hash
from backend.routers import auth, chat, documents, bookmarks, analytics, users, settings as settings_router
from backend.rag.document_loader import load_document
from backend.rag.text_splitter import split_text_into_chunks

app = FastAPI(
    title=f"{settings.ORG_NAME} - {settings.APP_NAME}",
    description="Enterprise AI School Knowledge Base & Grounded RAG Assistant",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(bookmarks.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(settings_router.router)

@app.on_event("startup")
def on_startup():
    """Initializes tables and seeds demo accounts & sample school documents."""
    init_db()
    db = SessionLocal()
    try:
        # 1. Seed Demo Accounts if not present
        demo_users = [
            ("admin", "admin@rsrtechnologies.co.in", "System Administrator", "Super Admin"),
            ("principal", "principal@rsrschool.edu", "Dr. Ramesh Sharma", "Principal"),
            ("teacher", "teacher@rsrschool.edu", "Ms. Anita Desai", "Teacher"),
            ("student", "student@rsrschool.edu", "Rahul Kumar", "Student"),
            ("parent", "parent@rsrschool.edu", "Mr. Vikram Rao", "Parent")
        ]
        for uname, email, fname, role in demo_users:
            existing = db.query(User).filter(User.username == uname).first()
            if not existing:
                u = User(
                    username=uname,
                    email=email,
                    full_name=fname,
                    role=role,
                    password_hash=get_password_hash("password123"),
                    is_active=True
                )
                db.add(u)
        db.commit()

        # 2. Seed Demo Documents from demo_documents/ or data/ if DB is empty
        doc_count = db.query(Document).count()
        if doc_count == 0:
            demo_dir = Path("./demo_documents")
            if demo_dir.exists():
                for fpath in demo_dir.glob("*.*"):
                    if fpath.suffix.lower() in [".pdf", ".docx", ".txt"]:
                        try:
                            pages, is_scanned, _ = load_document(fpath)
                            if pages and not is_scanned:
                                title = fpath.stem.replace("_", " ").title()
                                category = "Academic Policy" if "policy" in fpath.stem.lower() else ("Fee Structure" if "fee" in fpath.stem.lower() else "Student Handbook")
                                min_role = "Principal" if "confidential" in fpath.stem.lower() else "Student"
                                allowed_roles = ["Super Admin", "School Admin", "Principal", "Teacher", "Student", "Parent"]
                                
                                doc = Document(
                                    title=title,
                                    filename=fpath.name,
                                    file_path=str(fpath),
                                    category=category,
                                    file_type=fpath.suffix.replace(".", ""),
                                    file_size_kb=round(fpath.stat().st_size / 1024.0, 1),
                                    page_count=len(pages),
                                    chunk_count=0,
                                    min_role=min_role,
                                    uploaded_by="System Administrator",
                                    status="indexed"
                                )
                                db.add(doc)
                                db.commit()
                                db.refresh(doc)

                                chunks = split_text_into_chunks(
                                    pages=pages,
                                    doc_id=doc.id,
                                    doc_title=title,
                                    doc_category=category,
                                    academic_year="2024-2025",
                                    allowed_roles=allowed_roles,
                                    chunk_size=400,
                                    chunk_overlap=60
                                )
                                doc.chunk_count = len(chunks)
                                db.commit()

                                for idx, c in enumerate(chunks):
                                    chk = DocumentChunk(
                                        document_id=doc.id,
                                        chunk_index=idx,
                                        text=c.text,
                                        page_number=c.page_number,
                                        section=c.section,
                                        token_count=getattr(c, "token_count", 0)
                                    )
                                    db.add(chk)
                                db.commit()
                        except Exception as e:
                            print(f"Demo doc load notice ({fpath.name}): {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "organization": settings.ORG_NAME,
        "application": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "operational",
        "api_docs": "/api/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "SchoolGPT Backend", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
