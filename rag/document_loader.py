"""
SchoolGPT - Document Loader (PDF, DOCX, TXT)
Preserves page numbers, sections, and metadata.
Detects empty or scanned documents.
RSR Technologies
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import docx

# Try importing fitz (PyMuPDF)
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class DocumentPage:
    def __init__(self, text: str, page_number: int, section: str = "", metadata: Dict[str, Any] = None):
        self.text = text
        self.page_number = page_number
        self.section = section
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "page_number": self.page_number,
            "section": self.section,
            "metadata": self.metadata
        }

def load_pdf(file_path: Path) -> Tuple[List[DocumentPage], bool, str]:
    """
    Extracts text from PDF page-by-page using PyMuPDF (fitz).
    Returns (pages, is_scanned_or_empty, warning_message).
    """
    pages: List[DocumentPage] = []
    total_text_length = 0

    if not PYMUPDF_AVAILABLE:
        # Fallback to pypdf if fitz is not installed
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                total_text_length += len(text.strip())
                pages.append(DocumentPage(
                    text=text,
                    page_number=i + 1,
                    section=f"Page {i + 1}"
                ))
        except Exception as e:
            return [], False, f"Failed to extract PDF using pypdf: {str(e)}"
    else:
        try:
            doc = fitz.open(str(file_path))
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                text = page.get_text("text") or ""
                total_text_length += len(text.strip())
                
                # Check for table of contents or headings
                section_title = f"Page {page_idx + 1}"
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                if lines:
                    first_line = lines[0]
                    if len(first_line) < 60 and not first_line.isdigit():
                        section_title = first_line

                pages.append(DocumentPage(
                    text=text,
                    page_number=page_idx + 1,
                    section=section_title
                ))
            doc.close()
        except Exception as e:
            return [], False, f"Failed to extract PDF using PyMuPDF: {str(e)}"

    if len(pages) == 0:
        return [], True, "The PDF file contains no pages."

    if total_text_length < 50:
        return pages, True, (
            "Warning: This PDF document appears to contain scanned pages or image-only content with no extractable text. "
            "Optical Character Recognition (OCR) is required before this document can be indexed."
        )

    return pages, False, ""

def load_docx(file_path: Path) -> Tuple[List[DocumentPage], bool, str]:
    """
    Extracts text from DOCX document, grouping by headings/sections.
    """
    try:
        doc = docx.Document(str(file_path))
    except Exception as e:
        return [], False, f"Failed to load DOCX: {str(e)}"

    pages: List[DocumentPage] = []
    current_section = "General Section"
    current_text_buffer = []
    section_page_estimate = 1
    total_words = 0

    for paragraph in doc.paragraphs:
        p_text = paragraph.text.strip()
        if not p_text:
            continue

        total_words += len(p_text.split())

        # Check if heading
        if paragraph.style and paragraph.style.name.startswith("Heading"):
            if current_text_buffer:
                pages.append(DocumentPage(
                    text="\n".join(current_text_buffer),
                    page_number=section_page_estimate,
                    section=current_section
                ))
                current_text_buffer = []
                section_page_estimate += 1
            current_section = p_text
            current_text_buffer.append(p_text)
        else:
            current_text_buffer.append(p_text)

        # Split roughly every ~500 words if no headings to simulate pages
        if len(current_text_buffer) > 10 and len(" ".join(current_text_buffer).split()) > 500:
            pages.append(DocumentPage(
                text="\n".join(current_text_buffer),
                page_number=section_page_estimate,
                section=current_section
            ))
            current_text_buffer = []
            section_page_estimate += 1

    # Remaining text
    if current_text_buffer:
        pages.append(DocumentPage(
            text="\n".join(current_text_buffer),
            page_number=section_page_estimate,
            section=current_section
        ))

    # Also extract tables
    for table_idx, table in enumerate(doc.tables):
        table_rows = []
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            table_rows.append(" | ".join(row_data))
        if table_rows:
            section_page_estimate += 1
            pages.append(DocumentPage(
                text="\n".join(table_rows),
                page_number=section_page_estimate,
                section=f"Table {table_idx + 1}"
            ))

    if total_words < 10:
        return pages, True, "DOCX file contains almost no extractable text."

    return pages, False, ""

def load_txt(file_path: Path) -> Tuple[List[DocumentPage], bool, str]:
    """
    Extracts text from TXT file, segmenting into logical pages by double line breaks or markers.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return [], False, f"Failed to load TXT: {str(e)}"

    if not content.strip():
        return [], True, "TXT file is empty."

    # Split into sections by page markers or paragraph blocks
    raw_blocks = content.split("\n\n")
    pages: List[DocumentPage] = []
    current_page_text = []
    current_page_num = 1
    current_section = "Main Content"

    for block in raw_blocks:
        b_clean = block.strip()
        if not b_clean:
            continue

        # Look for custom page or section indicators like "=== Page 2 ===" or "[Section 4.2]"
        if b_clean.startswith("===") or b_clean.startswith("---") or b_clean.startswith("# "):
            if current_page_text:
                pages.append(DocumentPage(
                    text="\n\n".join(current_page_text),
                    page_number=current_page_num,
                    section=current_section
                ))
                current_page_text = []
                current_page_num += 1
            current_section = b_clean.strip("= -#").strip()
            current_page_text.append(b_clean)
        else:
            current_page_text.append(b_clean)
            if len("\n\n".join(current_page_text).split()) > 400:
                pages.append(DocumentPage(
                    text="\n\n".join(current_page_text),
                    page_number=current_page_num,
                    section=current_section
                ))
                current_page_text = []
                current_page_num += 1

    if current_page_text:
        pages.append(DocumentPage(
            text="\n\n".join(current_page_text),
            page_number=current_page_num,
            section=current_section
        ))

    return pages, False, ""

def load_document(file_path: Path) -> Tuple[List[DocumentPage], bool, str]:
    """
    Universal document loader router.
    Dispatches to appropriate loader based on file extension.
    """
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext in (".txt", ".md", ".csv"):
        return load_txt(file_path)
    else:
        return [], False, f"Unsupported file type: {ext}. Supported types: PDF, DOCX, TXT."
