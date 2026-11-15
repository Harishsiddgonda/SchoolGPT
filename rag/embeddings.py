"""
SchoolGPT - Embeddings Engine
Supports Ollama Embedding API (nomic-embed-text-v2-moe)
with high-performance on-device fallback vectorizer.
RSR Technologies
"""

import time
import math
import hashlib
import requests
from typing import List, Union
from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    EMBEDDING_DIMENSION
)

class EmbeddingService:
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model_name: str = OLLAMA_EMBED_MODEL,
        dimension: int = EMBEDDING_DIMENSION
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.dimension = dimension
        self._is_ollama_available = False
        self._last_check_time = 0
        self._cache_ttl_sec = 10.0  # Check status at most once every 10 seconds

    def check_ollama_available(self) -> bool:
        """Tests if Ollama embedding service is online and responding."""
        now = time.time()
        if now - self._last_check_time < self._cache_ttl_sec:
            return self._is_ollama_available

        self._last_check_time = now
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=1.0)
            if res.status_code == 200:
                self._is_ollama_available = True
                return True
        except Exception:
            pass
        self._is_ollama_available = False
        return False

    def get_status_info(self) -> dict:
        """Returns diagnostic info about embedding engine."""
        online = self.check_ollama_available()
        return {
            "engine": "Ollama Neural Embeddings" if online else "Local Deterministic Vectorizer",
            "model": self.model_name,
            "ollama_online": online,
            "dimension": self.dimension
        }

    def _fallback_vectorize(self, text: str) -> List[float]:
        """
        Deterministic, normalized n-gram hashed semantic embedding vector.
        Preserves lexical and semantic overlap between queries and documents.
        Dimension defaults to 768.
        """
        vec = [0.0] * self.dimension
        clean = text.lower().strip()
        if not clean:
            return vec

        # Tokenize words and character 3-grams
        words = clean.split()
        tokens = list(words)
        for w in words:
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    tokens.append(w[i:i+3])

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if ((h >> 4) & 1) else -1.0
            weight = math.log1p(len(token))
            vec[idx] += sign * weight

        # Normalize to unit vector for cosine similarity
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def embed_query(self, text: str) -> List[float]:
        """Generates embedding for a single query text."""
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of texts."""
        if not texts:
            return []

        # Check if Ollama is available before attempting network requests
        if not self.check_ollama_available():
            return [self._fallback_vectorize(t) for t in texts]

        # Try Ollama endpoint
        try:
            url = f"{self.base_url}/api/embeddings"
            results = []
            for t in texts:
                payload = {"model": self.model_name, "prompt": t}
                resp = requests.post(url, json=payload, timeout=2.0)
                if resp.status_code == 200:
                    embedding = resp.json().get("embedding")
                    if embedding and len(embedding) > 0:
                        results.append(embedding)
                    else:
                        raise ValueError("Empty embedding returned by Ollama")
                else:
                    raise ConnectionError(f"Ollama returned HTTP {resp.status_code}")
            return results
        except Exception:
            # Fallback immediately
            self._is_ollama_available = False
            return [self._fallback_vectorize(t) for t in texts]

# Singleton instance
embedding_service = EmbeddingService()
