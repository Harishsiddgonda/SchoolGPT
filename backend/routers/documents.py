"""
Document Management Router for SchoolGPT
Handles upload, indexing, listing, preview, and deletion with RBAC enforcement.
RSR Technologies
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User, Document, DocumentChunk
from backend.auth.dependencies import get_current_user, require_min_role, ROLE_HIERARCHY
from backend.rag.document_loader import load_document
from backend.rag.text_splitter import split_text_into_chunks
from rag.vector_store import vector_store

router = APIRouter(prefix="/api/documents", tags=["Documents & Knowledge Base"])

UPLOAD_DIR = Path("./data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("")
def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    user_weight = ROLE_HIERARCHY.get(current_user.role, 0)

    # Filter by user role permissions
    docs = query.all()
    filtered = []
    for doc in docs:
        doc_weight = ROLE_HIERARCHY.get(doc.min_role, 20)
        if user_weight >= doc_weight:
            # Apply category filter
            if category and category.lower() != "all" and doc.category.lower() != category.lower():
                continue
            # Apply search filter
            if search and search.lower() not in doc.title.lower() and search.lower() not in doc.filename.lower():
                continue
            filtered.append(doc.to_dict())

    return filtered

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: str = Form("General"),
    min_role: str = Form("Student"),
    current_user: User = Depends(require_min_role("Teacher")),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Supported: PDF, DOCX, TXT."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    clean_title = title.strip() if title and title.strip() else Path(file.filename).stem.replace("_", " ").title()
    save_filename = f"{int(os.times().elapsed)}_{file.filename}"
    dest_path = UPLOAD_DIR / save_filename

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    # Extract text using PyMuPDF / docx loader
    pages, is_scanned, warning_msg = load_document(dest_path)
    if not pages or is_scanned:
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=warning_msg or "Could not extract readable text from document."
        )

    # Save initial Document record to DB
    doc_record = Document(
        title=clean_title,
        filename=file.filename,
        file_path=str(dest_path),
        category=category,
        file_type=ext.replace(".", ""),
        file_size_kb=round(len(file_bytes) / 1024.0, 1),
        page_count=len(pages),
        chunk_count=0,
        min_role=min_role,
        uploaded_by=current_user.full_name,
        status="indexed"
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Split into chunks
    chunks = split_text_into_chunks(
        pages=pages,
        doc_id=doc_record.id,
        doc_title=clean_title,
        doc_category=category,
        academic_year="2024-2025",
        allowed_roles=[min_role, "Super Admin", "School Admin"],
        chunk_size=400,
        chunk_overlap=60
    )
    if not chunks:
        db.delete(doc_record)
        db.commit()
        raise HTTPException(status_code=400, detail="Failed to create semantic chunks from document.")

    doc_record.chunk_count = len(chunks)
    db.commit()

    # Save chunks to DB
    for chunk in chunks:
        chunk_record = DocumentChunk(
            document_id=doc_record.id,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            page_number=chunk.page_number,
            section=chunk.section,
            token_count=chunk.token_count
        )
        db.add(chunk_record)
    db.commit()

    # Index into vector store
    try:
        from rag.embeddings import embedding_service
        metadatas = []
        texts = []
        for c in chunks:
            texts.append(c.text)
            metadatas.append({
                "doc_id": doc_record.id,
                "doc_title": clean_title,
                "doc_category": category,
                "page_number": c.page_number,
                "section": c.section,
                "allowed_roles": [min_role, "Super Admin", "School Admin"]
            })
        vector_store.add_documents(
            texts=texts,
            metadatas=metadatas,
            doc_id=doc_record.id
        )
    except Exception as e:
        print(f"Notice: vector store indexing: {e}")

    return {
        "message": f"Successfully indexed '{clean_title}'",
        "document": doc_record.to_dict(),
        "chunks_indexed": len(chunks)
    }

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(require_min_role("Principal")),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        vector_store.delete_document(doc_id)
    except Exception:
        pass

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"message": f"Document '{doc.title}' deleted successfully"}

@router.get("/stats")
def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_docs = db.query(Document).count()
    total_chunks = db.query(DocumentChunk).count()
    
    docs = db.query(Document).all()
    category_counts = {}
    for d in docs:
        category_counts[d.category] = category_counts.get(d.category, 0) + 1

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "categories": category_counts
    }
