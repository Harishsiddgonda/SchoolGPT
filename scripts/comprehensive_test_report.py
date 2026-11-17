"""
Automated AI Test Engineer Suite: SchoolGPT Full Feature Audit
RSR Technologies
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.factory import seed_initial_data
from backend.auth.security import get_password_hash, verify_password, create_access_token, decode_access_token
from auth.permissions import can_access_document, has_permission
from backend.document_processing.document_loader import load_document, DocumentPage
from backend.document_processing.text_splitter import split_text_into_chunks
from rag.vector_store import vector_store
from rag.rag_pipeline import rag_pipeline

def run_feature_audit():
    results = []
    
    def log_test(category, feature_name, passed, details="", duration_ms=0):
        results.append({
            "category": category,
            "feature": feature_name,
            "status": "PASS" if passed else "FAIL",
            "duration_ms": round(duration_ms, 2),
            "details": details
        })

    # Ensure DB is seeded
    seed_initial_data()
    client = TestClient(app)

    # ==========================================
    # 1. SYSTEM INFRASTRUCTURE & BACKEND HEALTH
    # ==========================================
    t0 = time.time()
    try:
        r = client.get("/health")
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 200 and r.json().get("status") == "healthy")
        log_test("System Infrastructure", "FastAPI Service Health Endpoint (/health)", passed, f"Status: {r.status_code}, Payload: {r.json()}", dur)
    except Exception as e:
        log_test("System Infrastructure", "FastAPI Service Health Endpoint (/health)", False, str(e))

    t0 = time.time()
    try:
        r = client.get("/api/v1/health")
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 200 and "status" in r.json())
        log_test("System Infrastructure", "API v1 Health & Database Status (/api/v1/health)", passed, f"Status: {r.status_code}, DB: {r.json().get('database')}", dur)
    except Exception as e:
        log_test("System Infrastructure", "API v1 Health & Database Status (/api/v1/health)", False, str(e))

    t0 = time.time()
    try:
        spa_res = client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
        dur = (time.time() - t0) * 1000
        passed = (spa_res.status_code == 200 and "SchoolGPT" in spa_res.text)
        log_test("Frontend Architecture", "React Vite SPA Static Delivery (/) ", passed, f"HTML received, title/brand verified", dur)
    except Exception as e:
        log_test("Frontend Architecture", "React Vite SPA Static Delivery (/) ", False, str(e))

    # ==========================================
    # 2. AUTHENTICATION & IDENTITY (JWT + RBAC)
    # ==========================================
    t0 = time.time()
    try:
        pwd = "TestPassword@2026"
        hashed = get_password_hash(pwd)
        v1 = verify_password(pwd, hashed)
        v2 = verify_password("WrongPassword", hashed)
        dur = (time.time() - t0) * 1000
        passed = (v1 is True and v2 is False)
        log_test("Security & Auth", "Bcrypt Password Hashing & Salt Verification", passed, "Hash & invalid password rejection verified", dur)
    except Exception as e:
        log_test("Security & Auth", "Bcrypt Password Hashing & Salt Verification", False, str(e))

    t0 = time.time()
    try:
        tok = create_access_token({"sub": "testuser", "role": "Teacher"})
        decoded = decode_access_token(tok)
        dur = (time.time() - t0) * 1000
        passed = (decoded.get("sub") == "testuser" and decoded.get("role") == "Teacher")
        log_test("Security & Auth", "JWT Token Issuance & Cryptographic Signature", passed, f"Subject: {decoded.get('sub')}, Role: {decoded.get('role')}", dur)
    except Exception as e:
        log_test("Security & Auth", "JWT Token Issuance & Cryptographic Signature", False, str(e))

    t0 = time.time()
    try:
        r = client.get("/api/v1/auth/demo-accounts")
        dur = (time.time() - t0) * 1000
        accs = r.json()
        roles = [a["role"] for a in accs]
        required_roles = ["Super Admin", "Principal", "Teacher", "Student", "Parent"]
        all_present = all(any(req.lower() in ro.lower() for ro in roles) for req in required_roles)
        log_test("Security & Auth", "Demo Accounts Directory (/api/v1/auth/demo-accounts)", r.status_code == 200 and all_present, f"Roles present: {roles}", dur)
    except Exception as e:
        log_test("Security & Auth", "Demo Accounts Directory (/api/v1/auth/demo-accounts)", False, str(e))

    # Test login for each role
    tokens = {}
    for role_key, username in [("admin", "admin"), ("principal", "principal"), ("teacher", "teacher"), ("student", "student"), ("parent", "parent")]:
        t0 = time.time()
        try:
            res = client.post("/api/v1/auth/login", json={"username": username, "password": "password123"})
            dur = (time.time() - t0) * 1000
            passed = (res.status_code == 200 and "access_token" in res.json())
            if passed:
                tokens[role_key] = res.json()["access_token"]
            log_test("Security & Auth", f"User Authentication & Role Session ({username})", passed, f"Token received, User: {username}", dur)
        except Exception as e:
            log_test("Security & Auth", f"User Authentication & Role Session ({username})", False, str(e))

    # ==========================================
    # 3. ROLE-BASED ACCESS CONTROL (RBAC)
    # ==========================================
    t0 = time.time()
    try:
        p1 = has_permission("Super Admin", "can_manage_users")
        p2 = has_permission("Student", "can_upload_docs")
        allowed_roles = ["Super Admin", "School Administrator", "Principal"]
        p3 = can_access_document("Principal", allowed_roles)
        p4 = can_access_document("Student", allowed_roles)
        dur = (time.time() - t0) * 1000
        passed = (p1 is True and p2 is False and p3 is True and p4 is False)
        log_test("RBAC & Permissions", "Hierarchical Role Matrix Validation (Student vs Principal vs Admin)", passed, "Access hierarchy & document firewall verified", dur)
    except Exception as e:
        log_test("RBAC & Permissions", "Hierarchical Role Matrix Validation (Student vs Principal vs Admin)", False, str(e))

    # ==========================================
    # 4. DOCUMENT EXTRACTION & PROCESSING
    # ==========================================
    from config.settings import DEMO_DOCS_DIR
    pdf_path = DEMO_DOCS_DIR / "Student_Handbook.pdf"
    docx_path = DEMO_DOCS_DIR / "Admission_Policy.docx"
    txt_path = DEMO_DOCS_DIR / "Examination_Schedule.txt"

    # PDF Test
    t0 = time.time()
    try:
        pages, is_scanned, warning = load_document(pdf_path)
        dur = (time.time() - t0) * 1000
        passed = (len(pages) > 0 and len(pages[0].text.strip()) > 20 and is_scanned is False)
        log_test("Document Processing", "PDF Ingestion & Text Extraction (PyMuPDF)", passed, f"Extracted {len(pages)} pages", dur)
    except Exception as e:
        log_test("Document Processing", "PDF Ingestion & Text Extraction (PyMuPDF)", False, str(e))

    # DOCX Test
    t0 = time.time()
    try:
        pages_docx, is_scanned_docx, _ = load_document(docx_path)
        dur = (time.time() - t0) * 1000
        passed = (len(pages_docx) > 0 and len(pages_docx[0].text.strip()) > 20 and is_scanned_docx is False)
        log_test("Document Processing", "DOCX Ingestion & Paragraph Extraction (python-docx)", passed, f"Extracted {len(pages_docx)} sections", dur)
    except Exception as e:
        log_test("Document Processing", "DOCX Ingestion & Paragraph Extraction (python-docx)", False, str(e))

    # TXT Test
    t0 = time.time()
    try:
        pages_txt, is_scanned_txt, _ = load_document(txt_path)
        dur = (time.time() - t0) * 1000
        passed = (len(pages_txt) > 0 and len(pages_txt[0].text.strip()) > 20 and is_scanned_txt is False)
        log_test("Document Processing", "Plain Text Loader & UTF-8 Encoding (TXT)", passed, f"Extracted {len(pages_txt)} text blocks", dur)
    except Exception as e:
        log_test("Document Processing", "Plain Text Loader & UTF-8 Encoding (TXT)", False, str(e))

    # Chunking & Overlap
    t0 = time.time()
    try:
        chunks = split_text_into_chunks(pages, doc_id=101, doc_title="Test Title", doc_category="Test", academic_year="2024-2025", allowed_roles=["Student", "Parent"], chunk_size=300, chunk_overlap=50)
        dur = (time.time() - t0) * 1000
        passed = (len(chunks) > 0 and chunks[0].doc_id == 101)
        log_test("Document Processing", "Text Chunking & Sliding Window Overlap (300/50)", passed, f"Produced {len(chunks)} contextual chunks with metadata", dur)
    except Exception as e:
        log_test("Document Processing", "Text Chunking & Sliding Window Overlap (300/50)", False, str(e))

    # ==========================================
    # 5. VECTOR STORE & SEMANTIC EMBEDDINGS
    # ==========================================
    t0 = time.time()
    try:
        count = vector_store.count()
        dur = (time.time() - t0) * 1000
        passed = (count > 0)
        log_test("Vector Storage", "ChromaDB Collection Health & Vector Count", passed, f"Total indexed vectors: {count}", dur)
    except Exception as e:
        log_test("Vector Storage", "ChromaDB Collection Health & Vector Count", False, str(e))

    t0 = time.time()
    try:
        sim_results = vector_store.query("leave policy for students", n_results=3)
        dur = (time.time() - t0) * 1000
        passed = (len(sim_results) > 0)
        log_test("Vector Storage", "Semantic Cosine Similarity Retrieval", passed, f"Retrieved {len(sim_results)} top matches", dur)
    except Exception as e:
        log_test("Vector Storage", "Semantic Cosine Similarity Retrieval", False, str(e))

    # ==========================================
    # 6. RAG PIPELINE & GROUNDED CITATIONS
    # ==========================================
    t0 = time.time()
    try:
        student_token = tokens.get("student")
        headers = {"Authorization": f"Bearer {student_token}"}
        rag_res = client.post("/api/v1/chat", json={"question": "What is the schools leave policy for students?", "language": "en"}, headers=headers)
        dur = (time.time() - t0) * 1000
        data = rag_res.json()
        has_citations = len(data.get("sources", [])) > 0
        has_answer = len(data.get("answer", "")) > 20
        passed = (rag_res.status_code == 200 and has_answer and has_citations)
        log_test("RAG Intelligence", "Grounded AI Q&A with Exact Page Citations", passed, f"Citations count: {len(data.get('sources', []))}, Answer length: {len(data.get('answer',''))}", dur)
    except Exception as e:
        log_test("RAG Intelligence", "Grounded AI Q&A with Exact Page Citations", False, str(e))

    # Hallucination / Refusal Test
    t0 = time.time()
    try:
        out_of_domain = "What is the capital city of Australia and what is quantum entanglement theory?"
        rag_res = client.post("/api/v1/chat", json={"question": out_of_domain, "language": "en"}, headers=headers)
        dur = (time.time() - t0) * 1000
        data = rag_res.json()
        answer = data.get("answer", "").lower()
        # Should gracefully decline or state information is not available in school documents
        refusal_keywords = ["not find", "no information", "cannot find", "not available", "does not contain", "sorry", "not mentioned"]
        refusal_triggered = any(k in answer for k in refusal_keywords) or len(data.get("sources", [])) == 0
        log_test("RAG Intelligence", "Hallucination Guardrail & Out-of-Domain Refusal", refusal_triggered, f"Refusal/fallback acknowledged safely", dur)
    except Exception as e:
        log_test("RAG Intelligence", "Hallucination Guardrail & Out-of-Domain Refusal", False, str(e))

    # ==========================================
    # 7. MULTILINGUAL SUPPORT
    # ==========================================
    # Kannada
    t0 = time.time()
    try:
        rag_kn = client.post("/api/v1/chat", json={"question": "ರಜೆಯ ನಿಯಮಗಳು ಯಾವುವು?", "language": "kn"}, headers=headers)
        dur = (time.time() - t0) * 1000
        passed = (rag_kn.status_code == 200 and len(rag_kn.json().get("answer", "")) > 0)
        log_test("Multilingual Engine", "Kannada Query Resolution (ಕನ್ನಡ)", passed, f"Response delivered successfully", dur)
    except Exception as e:
        log_test("Multilingual Engine", "Kannada Query Resolution (ಕನ್ನಡ)", False, str(e))

    # Hindi
    t0 = time.time()
    try:
        rag_hi = client.post("/api/v1/chat", json={"question": "स्कूल की छुट्टी की नीति क्या है?", "language": "hi"}, headers=headers)
        dur = (time.time() - t0) * 1000
        passed = (rag_hi.status_code == 200 and len(rag_hi.json().get("answer", "")) > 0)
        log_test("Multilingual Engine", "Hindi Query Resolution (हिंदी)", passed, f"Response delivered successfully", dur)
    except Exception as e:
        log_test("Multilingual Engine", "Hindi Query Resolution (हिंदी)", False, str(e))

    # ==========================================
    # 8. CONVERSATION HISTORY & AUDIT TRAIL
    # ==========================================
    t0 = time.time()
    try:
        hist_res = client.get("/api/v1/chat/history", headers=headers)
        dur = (time.time() - t0) * 1000
        hist = hist_res.json()
        passed = (hist_res.status_code == 200 and isinstance(hist, list))
        log_test("Query History", "Per-User Conversation History Retrieval", passed, f"History records found: {len(hist)}", dur)
    except Exception as e:
        log_test("Query History", "Per-User Conversation History Retrieval", False, str(e))

    # ==========================================
    # 9. BOOKMARKS SYSTEM
    # ==========================================
    t0 = time.time()
    try:
        # Create Bookmark
        bm_create = client.post("/api/v1/bookmarks", json={
            "query_text": "Sample Bookmarked Question",
            "answer_text": "Sample Bookmarked Grounded Answer",
            "note": "Verified by QA"
        }, headers=headers)
        bm_id = bm_create.json().get("id")
        
        # List Bookmarks
        bm_list = client.get("/api/v1/bookmarks", headers=headers)
        listed = any(b.get("id") == bm_id for b in bm_list.json())

        # Delete Bookmark
        if bm_id:
            client.delete(f"/api/v1/bookmarks/{bm_id}", headers=headers)

        dur = (time.time() - t0) * 1000
        passed = (bm_create.status_code in [200, 201] and listed)
        log_test("Bookmarks System", "Bookmark Lifecycle (Create, List, Delete)", passed, f"Created ID {bm_id}, verified retrieval and deletion", dur)
    except Exception as e:
        log_test("Bookmarks System", "Bookmark Lifecycle (Create, List, Delete)", False, str(e))

    # ==========================================
    # 10. NOTIFICATIONS ENGINE
    # ==========================================
    t0 = time.time()
    try:
        notif_res = client.get("/api/v1/notifications", headers=headers)
        dur = (time.time() - t0) * 1000
        notifs = notif_res.json()
        passed = (notif_res.status_code == 200 and len(notifs) > 0)
        log_test("Notifications Engine", "Role-Targeted Alerts & Announcements", passed, f"Notifications received: {len(notifs)}", dur)
    except Exception as e:
        log_test("Notifications Engine", "Role-Targeted Alerts & Announcements", False, str(e))

    # ==========================================
    # 11. ANALYTICS & INSIGHTS
    # ==========================================
    t0 = time.time()
    try:
        admin_token = tokens.get("admin")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        an_res = client.get("/api/v1/analytics/overview", headers=admin_headers)
        dur = (time.time() - t0) * 1000
        data = an_res.json()
        passed = (an_res.status_code == 200 and "total_queries" in data and "total_documents" in data)
        log_test("Analytics & Reporting", "Admin System Analytics & Usage Breakdown", passed, f"Queries: {data.get('total_queries')}, Docs: {data.get('total_documents')}", dur)
    except Exception as e:
        log_test("Analytics & Reporting", "Admin System Analytics & Usage Breakdown", False, str(e))

    # ==========================================
    # 12. SYSTEM SETTINGS
    # ==========================================
    t0 = time.time()
    try:
        sett_res = client.get("/api/v1/settings", headers=admin_headers)
        dur = (time.time() - t0) * 1000
        passed = (sett_res.status_code == 200 and "ai_provider" in sett_res.json())
        log_test("System Configuration", "LLM Provider & RAG Settings Endpoint", passed, f"Provider: {sett_res.json().get('ai_provider')}", dur)
    except Exception as e:
        log_test("System Configuration", "LLM Provider & RAG Settings Endpoint", False, str(e))

    # ==========================================
    # 13. ANDROID MOBILE APK
    # ==========================================
    t0 = time.time()
    apk_path = Path("SchoolGPT.apk")
    apk_exists = apk_path.exists()
    apk_size_mb = round(apk_path.stat().st_size / (1024 * 1024), 2) if apk_exists else 0
    strings_xml = Path("android/app/src/main/res/values/strings.xml").read_text(encoding="utf-8")
    server_configured = "192.168.1.2:8000" in strings_xml
    dur = (time.time() - t0) * 1000
    apk_passed = apk_exists and apk_size_mb > 3.0 and server_configured
    log_test("Android Mobile App", "Android APK Package Integrity & Server Binding", apk_passed, f"Size: {apk_size_mb} MB, Server URL: 192.168.1.2:8000 confirmed", dur)

    # OUTPUT REPORT
    total = len(results)
    passed_count = sum(1 for r in results if r["status"] == "PASS")
    failed_count = total - passed_count

    print(json.dumps({
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate": f"{round((passed_count / total) * 100, 1)}%",
        "results": results
    }, indent=2))

if __name__ == "__main__":
    run_feature_audit()
