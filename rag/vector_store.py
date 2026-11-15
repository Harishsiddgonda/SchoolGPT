"""
SchoolGPT - Persistent ChromaDB Vector Store
Manages chunk storage, metadata indexing, semantic querying,
and document-level vector lifecycle.
RSR Technologies
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import CHROMA_PERSIST_DIR
from rag.text_splitter import TextChunk
from rag.embeddings import embedding_service

COLLECTION_NAME = "schoolgpt_documents"

class ChromaVectorStore:
    def __init__(self, persist_dir: Path = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "SchoolGPT Official School Knowledge Base", "hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[TextChunk]) -> int:
        """
        Embeds and stores text chunks with metadata into ChromaDB.
        """
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [c.to_metadata() for c in chunks]

        # Generate embeddings
        embeddings = embedding_service.embed_documents(texts)

        # Batch upsert to ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        return len(chunks)

    def delete_document_vectors(self, doc_id: int) -> int:
        """
        Deletes all vector chunks associated with a document ID.
        """
        try:
            # Query all items matching doc_id
            results = self.collection.get(
                where={"doc_id": int(doc_id)}
            )
            if results and results.get("ids"):
                ids_to_delete = results["ids"]
                self.collection.delete(ids=ids_to_delete)
                return len(ids_to_delete)
        except Exception:
            pass
        return 0

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        allowed_roles_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries ChromaDB using semantic embedding.
        Returns matched chunks with similarity scores and metadata.
        """
        query_vector = embedding_service.embed_query(query_text)
        
        # Query collection
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=min(n_results * 3, max(self.count(), 1)), # fetch extra to post-filter by role
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            return []

        if not results or not results.get("documents") or not results["documents"][0]:
            return []

        hits = []
        doc_texts = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(doc_texts)

        for i, text in enumerate(doc_texts):
            meta = metas[i] if i < len(metas) else {}
            dist = distances[i] if i < len(distances) else 1.0
            
            # ChromaDB cosine distance: similarity = 1.0 - (dist / 2) or 1.0 - dist
            # When distance is small, similarity is high
            similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

            roles_str = meta.get("allowed_roles_str", "")
            chunk_allowed_roles = [r.strip() for r in roles_str.split(",") if r.strip()]

            # Role filter verification
            if allowed_roles_filter:
                # User must have at least one allowed role matching chunk's allowed roles
                # Or user is Super Admin / School Administrator
                is_admin = any(r in ("Super Admin", "School Administrator") for r in allowed_roles_filter)
                if not is_admin:
                    has_role = any(r in chunk_allowed_roles for r in allowed_roles_filter)
                    if not has_role:
                        continue  # Skip unauthorized chunk

            hits.append({
                "chunk_id": meta.get("chunk_id", ""),
                "text": text,
                "similarity": round(similarity, 4),
                "distance": round(dist, 4),
                "doc_id": meta.get("doc_id"),
                "doc_title": meta.get("doc_title", "Document"),
                "doc_category": meta.get("doc_category", "General"),
                "page_number": meta.get("page_number", 1),
                "section": meta.get("section", ""),
                "academic_year": meta.get("academic_year", ""),
                "allowed_roles": chunk_allowed_roles
            })

            if len(hits) >= n_results:
                break

        return hits

    def count(self) -> int:
        """Returns total vector count in collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

    def reset_collection(self):
        """Clears all vectors in the collection."""
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "SchoolGPT Official School Knowledge Base", "hnsw:space": "cosine"}
        )

# Singleton vector store instance
vector_store = ChromaVectorStore()
