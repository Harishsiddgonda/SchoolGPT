"""
SQLAlchemy Models for SchoolGPT
RSR Technologies
"""

import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=True)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="Student")
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    queries = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    category = Column(String(64), default="General", index=True)
    file_type = Column(String(16), default="pdf")
    file_size_kb = Column(Float, default=0.0)
    page_count = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    min_role = Column(String(32), default="Student", index=True)
    uploaded_by = Column(String(64), default="Admin")
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(32), default="indexed")

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "category": self.category,
            "file_type": self.file_type,
            "file_size_kb": self.file_size_kb,
            "page_count": self.page_count,
            "chunk_count": self.chunk_count,
            "min_role": self.min_role,
            "uploaded_by": self.uploaded_by,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "status": self.status
        }


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    section = Column(String(128), default="")
    token_count = Column(Integer, default=0)
    # Stored as JSON string for cross-database compatibility (SQLite & PostgreSQL)
    embedding_json = Column(Text, nullable=True)

    document = relationship("Document", back_populates="chunks")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    language = Column(String(16), default="en")
    response_time_sec = Column(Float, default=0.0)
    model_used = Column(String(64), default="SchoolGPT Grounded Engine")
    sources_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="queries")
    bookmarks = relationship("Bookmark", back_populates="query")

    def to_dict(self):
        try:
            sources = json.loads(self.sources_json) if self.sources_json else []
        except Exception:
            sources = []
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query_text": self.query_text,
            "answer_text": self.answer_text,
            "language": self.language,
            "response_time_sec": self.response_time_sec,
            "model_used": self.model_used,
            "sources": sources,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_id = Column(Integer, ForeignKey("query_history.id", ondelete="SET NULL"), nullable=True)
    query_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    query = relationship("QueryHistory", back_populates="bookmarks")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "answer_text": self.answer_text,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query_id = Column(Integer, ForeignKey("query_history.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 (thumbs down) or 5 (thumbs up)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
