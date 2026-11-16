"""
SchoolGPT - Test Suite: Role-Based Retrieval & Isolation (RBAC)
Verifies that student accounts cannot access restricted fee/admin documents.
"""

from rag.rag_pipeline import rag_pipeline
from rag.retriever import retriever

def test_rbac_retrieval_student_vs_parent():
    query = "What is the annual tuition fee for Grade 9 and one-time charges?"

    # 1. As Parent (authorized for fee structure)
    parent_result = rag_pipeline.query(
        question=query,
        user_role="Parent",
        save_history=False
    )
    # Parent should get fee information
    parent_sources = [s["title"] for s in parent_result["sources"]]
    assert any("Fee" in s for s in parent_sources)
    assert "could not find reliable information" not in parent_result["answer"].lower()

    # 2. As Student (NOT authorized for School Fee Structure)
    student_result = rag_pipeline.query(
        question=query,
        user_role="Student",
        save_history=False
    )
    student_sources = [s["title"] for s in student_result["sources"]]
    # Student must NOT have retrieved the fee document
    assert not any("Fee Structure" in s for s in student_sources)

def test_rbac_admin_full_access():
    query = "What is the fee payment deadline?"
    admin_result = rag_pipeline.query(
        question=query,
        user_role="Super Admin",
        save_history=False
    )
    assert len(admin_result["sources"]) > 0
