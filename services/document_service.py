"""
SchoolGPT - Document Service
Handles file upload, validation, extraction, chunking,
indexing in ChromaDB, and document lifecycle.
RSR Technologies
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from config.settings import UPLOAD_DIR, DOCUMENT_CATEGORIES, ROLES, CHUNK_SIZE, CHUNK_OVERLAP
from database.models import (
    create_document,
    update_document_index_status,
    delete_document as db_delete_document,
    get_document_by_id,
    get_all_documents,
    log_activity
)
from rag.document_loader import load_document
from rag.text_splitter import split_text_into_chunks
from rag.vector_store import vector_store

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

class DocumentService:
    def __init__(self, upload_dir: Path = UPLOAD_DIR):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """Validates file extension and size."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file format '{ext}'. Only PDF, DOCX, and TXT files are supported."

        if file_size > MAX_FILE_SIZE_BYTES:
            return False, f"File size exceeds maximum allowed limit of 50 MB."

        if file_size <= 0:
            return False, "File is empty (0 bytes)."

        return True, ""

    def process_and_index_document(
        self,
        file_bytes: bytes,
        filename: str,
        title: str,
        category: str,
        academic_year: str,
        description: str,
        allowed_roles: List[str],
        uploaded_by_user_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Saves file, creates DB record, extracts text, chunks, embeds, and indexes into ChromaDB.
        """
        # Validate
        valid, msg = self.validate_file(filename, len(file_bytes))
        if not valid:
            return False, msg, None

        if not title.strip():
            title = Path(filename).stem.replace("_", " ").title()

        if not allowed_roles:
            allowed_roles = ROLES  # Default to all roles

        # Save file to uploads directory
        safe_filename = f"{academic_year}_{category.replace(' ', '_')}_{filename}"
        dest_path = self.upload_dir / safe_filename

        try:
            with open(dest_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            return False, f"Failed to save file: {str(e)}", None

        # Create database record
        file_type = Path(filename).suffix.lower().lstrip(".")
        doc_id = create_document(
            title=title,
            filename=safe_filename,
            file_path=str(dest_path),
            file_type=file_type,
            file_size_bytes=len(file_bytes),
            category=category,
            academic_year=academic_year,
            description=description,
            uploaded_by=uploaded_by_user_id,
            allowed_roles=allowed_roles
        )

        # Extract text
        pages, is_scanned, warning_msg = load_document(dest_path)
        if is_scanned and not pages:
            update_document_index_status(doc_id, 0, status="scanned_error")
            return False, warning_msg or "Document has no extractable text (scanned PDF).", doc_id

        # Split into chunks
        chunks = split_text_into_chunks(
            pages=pages,
            doc_id=doc_id,
            doc_title=title,
            doc_category=category,
            academic_year=academic_year,
            allowed_roles=allowed_roles,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        if not chunks:
            update_document_index_status(doc_id, 0, status="empty_error")
            return False, "No valid text chunks could be extracted from document.", doc_id

        # Index in ChromaDB
        try:
            indexed_count = vector_store.add_chunks(chunks)
            update_document_index_status(doc_id, indexed_count, status="indexed")
            log_activity(uploaded_by_user_id, "DOCUMENT_INDEXED", f"Indexed '{title}' ({indexed_count} chunks)")
            return True, f"Document '{title}' successfully indexed with {indexed_count} chunks.", doc_id
        except Exception as e:
            update_document_index_status(doc_id, 0, status="index_failed")
            return False, f"Indexing failed: {str(e)}", doc_id

    def delete_document(self, doc_id: int, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Deletes a document from SQLite, deletes its file from disk,
        and purges its vector embeddings from ChromaDB.
        """
        doc = get_document_by_id(doc_id)
        if not doc:
            return False, "Document not found."

        # Delete file from disk
        try:
            p = Path(doc["file_path"])
            if p.exists():
                p.unlink()
        except Exception:
            pass

        # Purge vector embeddings from ChromaDB
        deleted_chunks = vector_store.delete_document_vectors(doc_id)

        # Delete from SQLite
        db_delete_document(doc_id)
        log_activity(user_id, "DOCUMENT_DELETED", f"Deleted '{doc['title']}' (Purged {deleted_chunks} vectors)")

        return True, f"Document '{doc['title']}' and all associated vector records ({deleted_chunks} chunks) were deleted."

    def reindex_document(self, doc_id: int, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """Re-reads file from disk and re-indexes in ChromaDB."""
        doc = get_document_by_id(doc_id)
        if not doc:
            return False, "Document not found."

        file_path = Path(doc["file_path"])
        if not file_path.exists():
            return False, "Original file is missing from storage."

        # Delete existing vectors first
        vector_store.delete_document_vectors(doc_id)

        # Extract & chunk
        pages, is_scanned, warning = load_document(file_path)
        if is_scanned and not pages:
            return False, warning

        chunks = split_text_into_chunks(
            pages=pages,
            doc_id=doc_id,
            doc_title=doc["title"],
            doc_category=doc["category"],
            academic_year=doc["academic_year"],
            allowed_roles=doc.get("allowed_roles_list", ROLES),
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        indexed_count = vector_store.add_chunks(chunks)
        update_document_index_status(doc_id, indexed_count, status="indexed")
        log_activity(user_id, "DOCUMENT_REINDEXED", f"Re-indexed '{doc['title']}' ({indexed_count} chunks)")
        return True, f"Successfully re-indexed '{doc['title']}' with {indexed_count} chunks."

# Singleton instance
document_service = DocumentService()
