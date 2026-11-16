"""
SchoolGPT - Test Suite: Text Chunking and Metadata Preservation
"""

from rag.document_loader import DocumentPage
from rag.text_splitter import split_text_into_chunks

def test_chunking_metadata_preservation():
    sample_pages = [
        DocumentPage(text="This is page one text discussing school timings from 8:30 AM to 3:30 PM.", page_number=1, section="Section 1.1"),
        DocumentPage(text="This is page two text discussing leave policy and principal approval.", page_number=2, section="Section 4.2")
    ]

    chunks = split_text_into_chunks(
        pages=sample_pages,
        doc_id=101,
        doc_title="Student Rules",
        doc_category="School Policies",
        academic_year="2024-2025",
        allowed_roles=["Student", "Parent"],
        chunk_size=300,
        chunk_overlap=50
    )

    assert len(chunks) >= 2
    # Check that page numbers and doc metadata are attached to chunks
    assert chunks[0].page_number == 1
    assert chunks[0].doc_id == 101
    assert chunks[0].doc_title == "Student Rules"
    assert chunks[0].allowed_roles == ["Student", "Parent"]

    # Verify ChromaDB metadata converter
    meta = chunks[0].to_metadata()
    assert meta["page_number"] == 1
    assert meta["doc_id"] == 101
    assert meta["allowed_roles_str"] == "Student,Parent"
