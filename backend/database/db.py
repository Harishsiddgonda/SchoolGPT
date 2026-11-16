"""
Database Engine & Session Management for SchoolGPT
Compatible with PostgreSQL (pgvector on Render) and SQLite for local development.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

db_url = settings.DATABASE_URL
# Render provides postgres://, SQLAlchemy requires postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables and enables vector extension if PostgreSQL."""
    if db_url.startswith("postgresql"):
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
            except Exception as e:
                print(f"Notice: vector extension check: {e}")
    Base.metadata.create_all(bind=engine)
