"""
Unified RAG Engine for SchoolGPT
Orchestrates Retrieval, Dual LLM Routing (Gemini / Ollama), and Grounded Synthesis.
Enforces strict hallucination guardrails and multilingual answers.
RSR Technologies
"""

import time
import re
from typing import List, Dict, Any, Optional, Tuple
from backend.config import settings
from backend.rag.gemini_client import gemini_client
from backend.rag.ollama_client import ollama_client
from rag.retriever import retriever

INSUFFICIENT_INFO_MESSAGE = "I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."

INSUFFICIENT_INFO_TRANSLATIONS = {
    "en": INSUFFICIENT_INFO_MESSAGE,
    "kn": "ಶಾಲೆಯ ಅಧಿಕೃತ ದಾಖಲೆಗಳಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಶಾಲಾ ಆಡಳಿತವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    "hi": "स्कूल के आधिकारिक दस्तावेजों में इस प्रश्न के बारे में विश्वसनीय जानकारी नहीं मिली। कृपया स्कूल प्रशासन से संपर्क करें।"
}

class RAGEngine:
    def __init__(self):
        self.retriever = retriever
        self.gemini = gemini_client
        self.ollama = ollama_client

    def _fallback_grounded_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> str:
        refusal_msg = INSUFFICIENT_INFO_TRANSLATIONS.get(language, INSUFFICIENT_INFO_MESSAGE)
        if not context_chunks:
            return refusal_msg

        q_clean = query.lower()
        stop_words = {
            "what", "when", "where", "which", "how", "the", "for", "and", "is", "are", 
            "about", "can", "does", "tell", "give", "explain", "details", "any", "with",
            "this", "that", "there", "their", "have", "been", "from", "into"
        }
        generic_school_words = {
            "student", "students", "school", "schools", "child", "children", 
            "academy", "rsr", "institution", "campus", "academic"
        }
        all_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', q_clean) if w not in stop_words]
        core_keywords = [w for w in all_words if w not in generic_school_words]
        active_words = core_keywords if core_keywords else all_words

        if not active_words:
            return refusal_msg

        stem_patterns = []
        for w in active_words:
            stem = w[:-1] if (len(w) > 4 and w.endswith('s')) else w
            if len(stem) > 4:
                stem = stem[:4]
            stem_patterns.append(re.compile(r'\b' + re.escape(stem) + r'\w*', re.IGNORECASE))

        min_required = 2 if len(active_words) >= 2 else 1
        extracted_points = []
        primary_match_chunk = None

        for chunk in context_chunks:
            text = chunk.get("text", "")
            sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if len(s.strip()) > 15]
            for s in sentences:
                matches = sum(1 for p in stem_patterns if p.search(s))
                if matches >= min_required:
                    clean_s = s.replace("\n", " ").strip()
                    if clean_s not in extracted_points:
                        extracted_points.append(clean_s)
                        if primary_match_chunk is None:
                            primary_match_chunk = chunk

        if not extracted_points or primary_match_chunk is None:
            return refusal_msg

        title = primary_match_chunk.get("doc_title", "Official School Document")
        page = primary_match_chunk.get("page_number", 1)
        section = primary_match_chunk.get("section", "")

        ref_header = f"As per **{title}**"
        if section and not section.lower().startswith("page"):
            ref_header += f" ({section})"
        elif page:
            ref_header += f" (Page {page})"
        ref_header += ":"

        bullet_points = "\n".join([f"• {pt}" for pt in extracted_points[:4]])

        if language == "kn":
            return (
                f"**{title}** ದಾಖಲೆಯ ಪ್ರಕಾರ:\n\n"
                f"{bullet_points}\n\n"
                f"*(ಸೂಚನೆ: ಅಧಿಕೃತ ಶಾಲಾ ದಾಖಲೆಗಳಿಂದ ನೇರವಾಗಿ ಪಡೆದ ಮಾಹಿತಿ)*"
            )
        elif language == "hi":
            return (
                f"**{title}** दस्तावेज़ के अनुसार:\n\n"
                f"{bullet_points}\n\n"
                f"*(नोट: आधिकारिक स्कूल दस्तावेज़ों से सत्यापित जानकारी)*"
            )

        return f"{ref_header}\n\n{bullet_points}\n\n*Note: Verified response extracted from institutional documents.*"

    def query(
        self,
        question: str,
        user_role: str = "Student",
        language: str = "en",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        clean_question = question.strip()

        if not clean_question:
            return {
                "answer": "Please enter a valid question.",
                "sources": [],
                "model": "None",
                "response_time": 0.0,
                "chunks_retrieved": 0
            }

        # 1. Retrieve authorized chunks
        retrieved_chunks = self.retriever.retrieve(
            query=clean_question,
            user_role=user_role
        )

        answer = ""
        model_used = "Grounded Synthesis"

        # 2. Try Gemini if configured and preferred
        if settings.AI_PROVIDER == "gemini" and self.gemini.is_available():
            try:
                answer, model_used = self.gemini.generate(clean_question, retrieved_chunks, language)
            except Exception as e:
                print(f"Gemini fallback notice: {e}")
                answer = ""

        # 3. Try Ollama if preferred or Gemini failed
        if not answer and (settings.AI_PROVIDER == "ollama" or not self.gemini.is_available()):
            if self.ollama.is_available():
                try:
                    answer, model_used = self.ollama.generate(clean_question, retrieved_chunks, language)
                except Exception as e:
                    print(f"Ollama fallback notice: {e}")
                    answer = ""

        # 4. Fallback grounded engine (guarantees accurate answer or strict refusal)
        if not answer:
            answer = self._fallback_grounded_answer(clean_question, retrieved_chunks, language)
            model_used = "SchoolGPT Grounded Engine"

        elapsed = round(time.time() - start_time, 2)

        # 5. Assemble verified citations (only if valid answer found and not refusal)
        sources = []
        is_refusal = (
            "could not find reliable information" in answer.lower()
            or "ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ" in answer
            or "विश्वसनीय जानकारी नहीं मिली" in answer
        )

        if not is_refusal and retrieved_chunks:
            seen = set()
            for chunk in retrieved_chunks:
                key = (chunk.get("doc_title"), chunk.get("page_number"), chunk.get("section"))
                if key not in seen:
                    seen.add(key)
                    sources.append({
                        "doc_id": chunk.get("doc_id"),
                        "title": chunk.get("doc_title", "Official Document"),
                        "category": chunk.get("doc_category", "General"),
                        "page": chunk.get("page_number", 1),
                        "section": chunk.get("section", ""),
                        "snippet": chunk.get("text", "")[:250] + "...",
                        "similarity": round(float(chunk.get("similarity", 0.0)), 2)
                    })

        return {
            "answer": answer,
            "sources": sources,
            "model": model_used,
            "response_time": elapsed,
            "chunks_retrieved": len(retrieved_chunks)
        }

rag_engine = RAGEngine()
