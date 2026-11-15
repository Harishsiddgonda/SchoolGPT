"""
SchoolGPT - End-to-End RAG Pipeline Orchestrator
Coordinates retrieval, authorization, LLM synthesis, citation assembly,
and database history persistence.
RSR Technologies
"""

import time
from typing import Dict, Any, List, Optional
from rag.retriever import retriever
from rag.llm import llm_service
from database.models import save_query_history

class RAGPipeline:
    def __init__(self):
        self.retriever = retriever
        self.llm = llm_service

    def query(
        self,
        question: str,
        user_role: str,
        user_id: Optional[int] = None,
        language: str = "en",
        conversation_history: List[Dict[str, str]] = None,
        save_history: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete RAG query flow.
        """
        start_time = time.time()
        clean_question = question.strip()

        if not clean_question:
            return {
                "answer": "Please enter a valid question.",
                "sources": [],
                "model": "None",
                "response_time": 0.0,
                "query_id": None
            }

        # 1. Retrieve authorized chunks
        retrieved_chunks = self.retriever.retrieve(
            query=clean_question,
            user_role=user_role
        )

        # 2. Generate answer
        answer, model_used = self.llm.generate_answer(
            query=clean_question,
            context_chunks=retrieved_chunks,
            language=language,
            conversation_history=conversation_history
        )

        elapsed = round(time.time() - start_time, 2)

        # 3. Assemble unique source citations (only if valid answer found and not refusal)
        sources = []
        is_refusal = "could not find reliable information" in answer.lower() or "ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ" in answer or "विश्वसनीय जानकारी नहीं मिली" in answer

        if not is_refusal and retrieved_chunks:
            seen_sources = set()
            for chunk in retrieved_chunks:
                source_key = (chunk.get("doc_title"), chunk.get("page_number"), chunk.get("section"))
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    sources.append({
                        "doc_id": chunk.get("doc_id"),
                        "title": chunk.get("doc_title", "Official Document"),
                        "category": chunk.get("doc_category", "General"),
                        "page": chunk.get("page_number", 1),
                        "section": chunk.get("section", ""),
                        "snippet": chunk.get("text", "")[:250] + "...",
                        "similarity": chunk.get("similarity", 0.0)
                    })

        # 4. Save to database query history if user_id is provided
        query_id = None
        if save_history and user_id is not None:
            try:
                query_id = save_query_history(
                    user_id=user_id,
                    query_text=clean_question,
                    answer_text=answer,
                    language=language,
                    response_time_sec=elapsed,
                    sources=sources
                )
            except Exception:
                pass

        return {
            "answer": answer,
            "sources": sources,
            "model": model_used,
            "response_time": elapsed,
            "query_id": query_id,
            "chunks_retrieved": len(retrieved_chunks)
        }

# Singleton RAG pipeline instance
rag_pipeline = RAGPipeline()
