"""
SchoolGPT - Database Models & Data Access Layer
RSR Technologies
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from database.db import query_one, query_all, execute_insert, execute_update

# ================= USER REPOSITORY =================

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM users WHERE id = ?", (user_id,))

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM users WHERE username = ?", (username,))

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM users WHERE email = ?", (email,))

def get_all_users() -> List[Dict[str, Any]]:
    return query_all("SELECT id, username, email, full_name, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC")

def create_user(username: str, email: str, full_name: str, role: str, password_hash: str) -> int:
    sql = """
        INSERT INTO users (username, email, full_name, role, password_hash, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """
    return execute_insert(sql, (username.strip(), email.strip().lower(), full_name.strip(), role, password_hash))

def update_user_status(user_id: int, is_active: bool) -> int:
    return execute_update("UPDATE users SET is_active = ? WHERE id = ?", (1 if is_active else 0, user_id))

def update_user_role(user_id: int, role: str) -> int:
    return execute_update("UPDATE users SET role = ? WHERE id = ?", (role, user_id))

def update_user_password(user_id: int, password_hash: str) -> int:
    return execute_update("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))

def update_last_login(user_id: int) -> int:
    return execute_update("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))

def delete_user(user_id: int) -> int:
    return execute_update("DELETE FROM users WHERE id = ?", (user_id,))

# ================= DOCUMENT REPOSITORY =================

def create_document(
    title: str,
    filename: str,
    file_path: str,
    file_type: str,
    file_size_bytes: int,
    category: str,
    academic_year: str,
    description: str,
    uploaded_by: Optional[int],
    allowed_roles: List[str]
) -> int:
    sql = """
        INSERT INTO documents (
            title, filename, file_path, file_type, file_size_bytes,
            category, academic_year, description, uploaded_by, allowed_roles,
            chunk_count, is_indexed, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 'processing')
    """
    roles_json = json.dumps(allowed_roles)
    doc_id = execute_insert(sql, (
        title, filename, str(file_path), file_type.lower(), file_size_bytes,
        category, academic_year, description, uploaded_by, roles_json
    ))
    # Insert role permissions
    for role in allowed_roles:
        execute_insert("INSERT INTO document_access (document_id, role) VALUES (?, ?)", (doc_id, role))
    return doc_id

def update_document_index_status(doc_id: int, chunk_count: int, status: str = "indexed"):
    is_indexed = 1 if status == "indexed" else 0
    execute_update(
        "UPDATE documents SET chunk_count = ?, is_indexed = ?, status = ? WHERE id = ?",
        (chunk_count, is_indexed, status, doc_id)
    )

def get_document_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    row = query_one("SELECT * FROM documents WHERE id = ?", (doc_id,))
    if row and "allowed_roles" in row and isinstance(row["allowed_roles"], str):
        try:
            row["allowed_roles_list"] = json.loads(row["allowed_roles"])
        except Exception:
            row["allowed_roles_list"] = []
    return row

def get_all_documents() -> List[Dict[str, Any]]:
    rows = query_all("""
        SELECT d.*, u.full_name as uploader_name 
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        ORDER BY d.upload_date DESC
    """)
    for r in rows:
        try:
            r["allowed_roles_list"] = json.loads(r.get("allowed_roles", "[]"))
        except Exception:
            r["allowed_roles_list"] = []
    return rows

def get_accessible_documents(user_role: str) -> List[Dict[str, Any]]:
    """Returns documents accessible by the specific user role."""
    all_docs = get_all_documents()
    if user_role in ("Super Admin", "School Administrator"):
        return all_docs
    return [d for d in all_docs if user_role in d.get("allowed_roles_list", [])]

def delete_document(doc_id: int) -> int:
    execute_update("DELETE FROM document_access WHERE document_id = ?", (doc_id,))
    return execute_update("DELETE FROM documents WHERE id = ?", (doc_id,))

# ================= QUERY HISTORY REPOSITORY =================

def save_query_history(
    user_id: int,
    query_text: str,
    answer_text: str,
    language: str = "en",
    response_time_sec: float = 0.0,
    sources: List[Dict[str, Any]] = None,
    tokens_used: int = 0,
    conversation_id: Optional[int] = None
) -> int:
    sources_json = json.dumps(sources or [])
    sql = """
        INSERT INTO query_history (
            user_id, conversation_id, query_text, answer_text,
            language, response_time_sec, sources_json, tokens_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    return execute_insert(sql, (
        user_id, conversation_id, query_text, answer_text,
        language, response_time_sec, sources_json, tokens_used
    ))

def get_user_query_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    rows = query_all("""
        SELECT * FROM query_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    for r in rows:
        try:
            r["sources"] = json.loads(r.get("sources_json", "[]"))
        except Exception:
            r["sources"] = []
    return rows

def delete_query_history_item(query_id: int, user_id: int) -> int:
    return execute_update("DELETE FROM query_history WHERE id = ? AND user_id = ?", (query_id, user_id))

def clear_user_query_history(user_id: int) -> int:
    return execute_update("DELETE FROM query_history WHERE user_id = ?", (user_id,))

# ================= BOOKMARKS REPOSITORY =================

def add_bookmark(
    user_id: int,
    question: str,
    answer: str,
    category: str = "General",
    title: Optional[str] = None,
    sources: List[Dict[str, Any]] = None,
    query_history_id: Optional[int] = None
) -> int:
    if not title:
        title = question[:50] + ("..." if len(question) > 50 else "")
    sources_json = json.dumps(sources or [])
    sql = """
        INSERT INTO bookmarks (
            user_id, query_history_id, title, category, question, answer, sources_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return execute_insert(sql, (user_id, query_history_id, title, category, question, answer, sources_json))

def get_user_bookmarks(user_id: int) -> List[Dict[str, Any]]:
    rows = query_all("""
        SELECT * FROM bookmarks 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))
    for r in rows:
        try:
            r["sources"] = json.loads(r.get("sources_json", "[]"))
        except Exception:
            r["sources"] = []
    return rows

def delete_bookmark(bookmark_id: int, user_id: int) -> int:
    return execute_update("DELETE FROM bookmarks WHERE id = ? AND user_id = ?", (bookmark_id, user_id))

# ================= FEEDBACK & ACTIVITY =================

def record_feedback(query_history_id: int, user_id: int, rating: int, comments: str = "") -> int:
    sql = "INSERT INTO feedback (query_history_id, user_id, rating, comments) VALUES (?, ?, ?, ?)"
    return execute_insert(sql, (query_history_id, user_id, rating, comments))

def log_activity(user_id: Optional[int], action: str, details: str = "", ip_address: str = "127.0.0.1") -> int:
    sql = "INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)"
    return execute_insert(sql, (user_id, action, details, ip_address))

def get_recent_activity(limit: int = 50) -> List[Dict[str, Any]]:
    return query_all("""
        SELECT a.*, u.username, u.role 
        FROM activity_logs a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """, (limit,))

# ================= SETTINGS REPOSITORY =================

def get_setting(key: str, default: str = "") -> str:
    row = query_one("SELECT value FROM application_settings WHERE key = ?", (key,))
    return row["value"] if row else default

def set_setting(key: str, value: str, description: str = ""):
    execute_update("""
        INSERT INTO application_settings (key, value, description, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
    """, (key, value, description))

def get_all_settings() -> Dict[str, str]:
    rows = query_all("SELECT key, value FROM application_settings")
    return {r["key"]: r["value"] for r in rows}

# ================= ANALYTICS METRICS =================

def get_dashboard_metrics() -> Dict[str, Any]:
    docs_count = query_one("SELECT COUNT(*) as c, SUM(file_size_bytes) as total_size FROM documents")
    users_count = query_one("SELECT COUNT(*) as c, SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) as active FROM users")
    queries_count = query_one("SELECT COUNT(*) as c FROM query_history")
    answered_count = query_one("""
        SELECT COUNT(*) as c FROM query_history 
        WHERE answer_text NOT LIKE '%could not find reliable information%'
    """)
    
    total_size = docs_count["total_size"] or 0
    size_str = f"{total_size / (1024*1024):.1f} MB" if total_size > 1024*1024 else f"{total_size / 1024:.1f} KB"

    return {
        "total_documents": docs_count["c"] or 0,
        "total_users": users_count["c"] or 0,
        "active_users": users_count["active"] or 0,
        "total_questions": queries_count["c"] or 0,
        "questions_answered": answered_count["c"] or 0,
        "kb_size": size_str,
        "kb_size_bytes": total_size
    }
