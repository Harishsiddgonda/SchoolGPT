"""
SchoolGPT - Database Connection and Initialization
RSR Technologies
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from config.settings import DATABASE_PATH, BASE_DIR

SCHEMA_FILE = BASE_DIR / "database" / "schema.sql"

def get_connection():
    """Returns a new SQLite connection with Row factory enabled."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    """Context manager for database transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initializes the database schema if not already present."""
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_FILE}")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)
        # Initialize default settings if not exists
        default_settings = [
            ("school_name", "RSR International Academy", "Official School Name"),
            ("academic_year", "2024-2025", "Current Academic Year"),
            ("contact_email", "support@rsrtechnologies.co.in", "School Admin Contact Email"),
            ("contact_phone", "+91 99453 21367 / +91 77605 94868", "Official Contact Numbers"),
            ("website", "www.rsrtechnologies.co.in", "Official Website URL"),
            ("ollama_status", "configured", "LLM Integration Status"),
            ("rag_mode", "standard", "Active RAG Mode")
        ]
        for key, val, desc in default_settings:
            conn.execute(
                "INSERT OR IGNORE INTO application_settings (key, value, description) VALUES (?, ?, ?)",
                (key, val, desc)
            )

def query_one(sql: str, params: tuple = ()):
    """Convenience helper to query a single record as dict."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def query_all(sql: str, params: tuple = ()):
    """Convenience helper to query multiple records as list of dicts."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def execute_insert(sql: str, params: tuple = ()) -> int:
    """Executes an INSERT statement and returns the inserted row ID."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid

def execute_update(sql: str, params: tuple = ()) -> int:
    """Executes an UPDATE/DELETE statement and returns affected rows count."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return cursor.rowcount
