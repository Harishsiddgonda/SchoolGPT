"""
SchoolGPT - Test Suite: RAG Pipeline, Grounding & Refusal Logic
"""

import pytest
from rag.rag_pipeline import rag_pipeline
from database.models import add_bookmark, get_user_bookmarks, delete_bookmark

def test_rag_grounded_answer_with_citations():
    # Question covered in Student Handbook / Leave Policy
    question = "What is the schools leave policy for students?"
    result = rag_pipeline.query(
        question=question,
        user_role="Parent",
        save_history=False
    )

    assert result["answer"] is not None
    assert len(result["sources"]) > 0

    # Verify citation fields
    first_source = result["sources"][0]
    assert "title" in first_source
    assert "page" in first_source
    assert "snippet" in first_source
    assert first_source["page"] is not None

def test_refusal_when_information_unavailable():
    # Question completely outside school documents
    out_of_domain_question = "What is the interest rate for a home loan at the state bank?"
    result = rag_pipeline.query(
        question=out_of_domain_question,
        user_role="Student",
        save_history=False
    )

    # Must return exact insufficient info message
    assert "could not find reliable information" in result["answer"].lower()
    # Must NOT fabricate citations
    assert len(result["sources"]) == 0

def test_bookmark_lifecycle():
    user_id = 1
    bm_id = add_bookmark(
        user_id=user_id,
        question="What is the exam pass benchmark?",
        answer="Grade D (33%) is the minimum benchmark.",
        category="Examinations"
    )
    assert bm_id > 0

    user_bms = get_user_bookmarks(user_id=user_id)
    assert any(b["id"] == bm_id for b in user_bms)

    # Delete bookmark
    del_count = delete_bookmark(bm_id, user_id=user_id)
    assert del_count == 1
