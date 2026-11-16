"""
SchoolGPT - Text Splitter with Metadata Preservation
Splits document text into overlapping semantic chunks
while preserving page numbers, section titles, and roles.
RSR Technologies
"""

import re
from typing import List, Dict, Any
from rag.document_loader import DocumentPage

class TextChunk:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        page_number: int,
        section: str,
        doc_id: int,
        doc_title: str,
        doc_category: str,
        academic_year: str,
        allowed_roles: List[str]
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.page_number = page_number
        self.section = section
        self.doc_id = doc_id
        self.doc_title = doc_title
        self.doc_category = doc_category
        self.academic_year = academic_year
        self.allowed_roles = allowed_roles

    def to_metadata(self) -> Dict[str, Any]:
        """Returns metadata dictionary suitable for ChromaDB."""
        return {
            "chunk_id": self.chunk_id,
            "page_number": int(self.page_number),
            "section": str(self.section),
            "doc_id": int(self.doc_id),
            "doc_title": str(self.doc_title),
            "doc_category": str(self.doc_category),
            "academic_year": str(self.academic_year),
            "allowed_roles_str": ",".join(self.allowed_roles)
        }

def split_text_into_chunks(
    pages: List[DocumentPage],
    doc_id: int,
    doc_title: str,
    doc_category: str,
    academic_year: str,
    allowed_roles: List[str],
    chunk_size: int = 600,
    chunk_overlap: int = 100
) -> List[TextChunk]:
    """
    Chunks text page-by-page to ensure page number accuracy.
    If a page is smaller than chunk_size, it forms a single chunk.
    If larger, it is split with overlap.
    """
    chunks: List[TextChunk] = []
    chunk_global_counter = 0

    for page in pages:
        page_text = page.text.strip()
        if not page_text:
            continue

        words = page_text.split()
        if not words:
            continue

        # If page is short, keep as single chunk
        if len(page_text) <= chunk_size:
            chunk_global_counter += 1
            chunk_id = f"doc_{doc_id}_p{page.page_number}_c{chunk_global_counter}"
            chunks.append(TextChunk(
                chunk_id=chunk_id,
                text=page_text,
                page_number=page.page_number,
                section=page.section,
                doc_id=doc_id,
                doc_title=doc_title,
                doc_category=doc_category,
                academic_year=academic_year,
                allowed_roles=allowed_roles
            ))
            continue

        # Split into sentence or word windows
        # Let's split by sentences or paragraphs first
        sentences = re.split(r'(?<=[.!?\n])\s+', page_text)
        current_chunk_words = []
        current_char_count = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_len = len(sentence)
            if current_char_count + sentence_len > chunk_size and current_chunk_words:
                chunk_str = " ".join(current_chunk_words)
                chunk_global_counter += 1
                chunk_id = f"doc_{doc_id}_p{page.page_number}_c{chunk_global_counter}"
                chunks.append(TextChunk(
                    chunk_id=chunk_id,
                    text=chunk_str,
                    page_number=page.page_number,
                    section=page.section,
                    doc_id=doc_id,
                    doc_title=doc_title,
                    doc_category=doc_category,
                    academic_year=academic_year,
                    allowed_roles=allowed_roles
                ))

                # Handle overlap: retain trailing words
                overlap_words = []
                overlap_chars = 0
                for w in reversed(current_chunk_words):
                    overlap_chars += len(w) + 1
                    overlap_words.insert(0, w)
                    if overlap_chars >= chunk_overlap:
                        break
                current_chunk_words = overlap_words
                current_char_count = sum(len(w) + 1 for w in current_chunk_words)

            current_chunk_words.append(sentence)
            current_char_count += sentence_len + 1

        if current_chunk_words:
            chunk_str = " ".join(current_chunk_words)
            chunk_global_counter += 1
            chunk_id = f"doc_{doc_id}_p{page.page_number}_c{chunk_global_counter}"
            chunks.append(TextChunk(
                chunk_id=chunk_id,
                text=chunk_str,
                page_number=page.page_number,
                section=page.section,
                doc_id=doc_id,
                doc_title=doc_title,
                doc_category=doc_category,
                academic_year=academic_year,
                allowed_roles=allowed_roles
            ))

    return chunks
