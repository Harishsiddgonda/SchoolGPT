"""
SchoolGPT - Test Suite: Document Extraction & Loaders
"""

import pytest
from pathlib import Path
from rag.document_loader import load_document, DocumentPage
from config.settings import DEMO_DOCS_DIR

def test_load_pdf_extraction():
    pdf_path = DEMO_DOCS_DIR / "Student_Handbook.pdf"
    assert pdf_path.exists(), "Student_Handbook.pdf should exist in demo_documents"

    pages, is_scanned, warning = load_document(pdf_path)
    assert is_scanned is False
    assert len(pages) > 0
    # Verify page numbers are preserved
    for i, p in enumerate(pages, 1):
        assert p.page_number == i
        assert len(p.text.strip()) > 0

    combined_text = " ".join(p.text for p in pages)
    assert "8:30 AM" in combined_text or "Attendance" in combined_text

def test_load_docx_extraction():
    docx_path = DEMO_DOCS_DIR / "Admission_Policy.docx"
    assert docx_path.exists(), "Admission_Policy.docx should exist"

    pages, is_scanned, warning = load_document(docx_path)
    assert is_scanned is False
    assert len(pages) > 0
    combined_text = " ".join(p.text for p in pages)
    assert "Birth Certificate" in combined_text or "Admission" in combined_text

def test_load_txt_extraction():
    txt_path = DEMO_DOCS_DIR / "Examination_Schedule.txt"
    assert txt_path.exists(), "Examination_Schedule.txt should exist"

    pages, is_scanned, warning = load_document(txt_path)
    assert is_scanned is False
    assert len(pages) > 0
    combined_text = " ".join(p.text for p in pages)
    assert "Mid-Term" in combined_text or "Examination" in combined_text

def test_scanned_or_empty_detection(tmp_path):
    empty_file = tmp_path / "empty_doc.txt"
    empty_file.write_text("", encoding="utf-8")

    pages, is_scanned, warning = load_document(empty_file)
    assert is_scanned is True
    assert "empty" in warning.lower()
