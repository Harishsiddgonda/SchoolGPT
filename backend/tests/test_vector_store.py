"""
SchoolGPT - Test Suite: ChromaDB Vector Store & Vector Lifecycle
"""

import pytest
from rag.text_splitter import TextChunk
from rag.vector_store import vector_store

def test_vector_store_add_and_query():
    chunks = [
        TextChunk(
            chunk_id="test_doc_999_c1",
            text="The annual science exhibition will be conducted in the secondary auditorium on December 15.",
            page_number=1,
            section="Events",
            doc_id=999,
            doc_title="Test Science Circular",
            doc_category="School Circulars",
            academic_year="2024-2025",
            allowed_roles=["Teacher", "Student", "Parent"]
        )
    ]

    added = vector_store.add_chunks(chunks)
    assert added == 1

    # Query for the topic
    hits = vector_store.query("When is the annual science exhibition scheduled?", n_results=3)
    assert len(hits) > 0
    matched_ids = [h["chunk_id"] for h in hits]
    assert "test_doc_999_c1" in matched_ids

def test_vector_deletion_lifecycle():
    # Purge test document 999
    deleted = vector_store.delete_document_vectors(doc_id=999)
    assert deleted >= 1

    # Query again and verify it is gone
    hits = vector_store.query("When is the annual science exhibition scheduled?", n_results=3)
    matched_ids = [h["chunk_id"] for h in hits]
    assert "test_doc_999_c1" not in matched_ids
