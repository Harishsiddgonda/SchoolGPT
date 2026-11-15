"""
SchoolGPT - Context Retriever & Role-Based Filtering
Retrieves relevant knowledge chunks with strict role gating.
RSR Technologies
"""

from typing import List, Dict, Any, Optional
from config.settings import TOP_K_RESULTS, SIMILARITY_THRESHOLD
from rag.vector_store import vector_store

class Retriever:
    def __init__(
        self,
        top_k: int = TOP_K_RESULTS,
        threshold: float = SIMILARITY_THRESHOLD
    ):
        self.top_k = top_k
        self.threshold = threshold

    def retrieve(
        self,
        query: str,
        user_role: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant chunks for `query` authorized for `user_role`.
        """
        limit = top_k or self.top_k
        min_sim = threshold if threshold is not None else self.threshold

        # Pass user role filter list
        allowed_roles_filter = [user_role]
        if user_role in ("Super Admin", "School Administrator"):
            allowed_roles_filter = None  # Full access

        raw_hits = vector_store.query(
            query_text=query,
            n_results=limit,
            allowed_roles_filter=allowed_roles_filter
        )

        # Filter by minimum similarity score
        filtered_hits = [h for h in raw_hits if h["similarity"] >= min_sim]

        # Format citations
        for hit in filtered_hits:
            page = hit.get("page_number", 1)
            section = hit.get("section", "")
            title = hit.get("doc_title", "Official Document")

            citation_label = f"{title}"
            if page:
                citation_label += f" (Page {page}"
                if section and not section.lower().startswith("page"):
                    citation_label += f", Section: {section}"
                citation_label += ")"

            hit["citation_label"] = citation_label

        return filtered_hits

# Singleton instance
retriever = Retriever()
