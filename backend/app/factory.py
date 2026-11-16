"""
FastAPI Application Factory with Modern Lifespan
Organization: RSR Technologies
Tagline: Smart. Reliable. Instant Answers.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import settings
from backend.database.db import init_db, SessionLocal
from backend.models.models import User, Document, DocumentChunk
from backend.auth.security import get_password_hash
from backend.document_processing.document_loader import load_document
from backend.document_processing.text_splitter import split_text_into_chunks
from backend.api.v1.router import api_v1_router
from backend.routers import auth, chat, documents, bookmarks, analytics, users, settings as settings_router

def seed_initial_data():
    """Initializes tables and seeds demo accounts & sample school documents."""
    init_db()
    db = SessionLocal()
    try:
        # 1. Seed Demo Accounts
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

        # 2. Seed Demo Documents if DB is empty
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
                            print(f"Notice during demo doc seeding: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed Database
    seed_initial_data()
    yield
    # Shutdown

def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.ORG_NAME} - {settings.APP_NAME}",
        description="Enterprise AI School Knowledge Base & Grounded RAG Assistant",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount v1 Router (/api/v1/...)
    app.include_router(api_v1_router)

    # Mount Root Routers (/api/...) for backward compatibility
    app.include_router(auth.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(bookmarks.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(settings_router.router, prefix="/api")

    dist_dir = Path("apps/web/dist")
    if dist_dir.exists():
        assets_dir = dist_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static_assets")

    @app.get("/")
    def root(request: Request):
        dist_index = dist_dir / "index.html"
        accept = request.headers.get("accept", "")
        user_agent = request.headers.get("user-agent", "")
        is_browser = "text/html" in accept or "Mozilla" in user_agent or "SchoolGPT" in user_agent
        is_explicit_json = "application/json" in accept and "text/html" not in accept

        if dist_index.exists() and is_browser and not is_explicit_json:
            return FileResponse(dist_index)

        return {
            "organization": settings.ORG_NAME,
            "application": settings.APP_NAME,
            "tagline": settings.TAGLINE,
            "version": settings.VERSION,
            "status": "operational",
            "api_v1": "/api/v1",
            "api_docs": "/api/docs"
        }

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "SchoolGPT Backend", "version": settings.VERSION}

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Do not catch /api or /health routes
        if full_path.startswith("api/") or full_path == "health":
            return {"detail": "Not Found"}
        file_candidate = dist_dir / full_path
        if file_candidate.is_file():
            return FileResponse(file_candidate)
        dist_index = dist_dir / "index.html"
        if dist_index.exists():
            return FileResponse(dist_index)
        return {"detail": "Not Found"}

    return app
