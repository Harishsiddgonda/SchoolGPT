"""
Ollama Client for SchoolGPT
Communicates with local Ollama service (Qwen3:4b / Llama3 / Mistral).
RSR Technologies
"""

import requests
from typing import List, Dict, Any, Tuple
from backend.config import settings

class OllamaClient:
    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model_name: str = settings.OLLAMA_LLM_MODEL
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def is_available(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=1.0)
            return res.status_code == 200
        except Exception:
            return False

    def generate(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> Tuple[str, str]:
        context_blocks = []
        for i, chunk in enumerate(context_chunks, 1):
            title = chunk.get("doc_title", "Document")
            page = chunk.get("page_number", 1)
            section = chunk.get("section", "")
            text = chunk.get("text", "").strip()
            header = f"[Source {i}: {title} | Page {page}"
            if section:
                header += f" | Section: {section}"
            header += "]"
            context_blocks.append(f"{header}\n{text}")

        context_str = "\n\n---\n\n".join(context_blocks)
        prompt = f"""You are SchoolGPT for RSR Technologies. Answer strictly from the school context below.
If the context does not contain the answer, reply:
"I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."

Language: {language}
Official Context:
{context_str}

Question: {query}
Answer:"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 700
            }
        }

        try:
            res = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30.0
            )
            if res.status_code == 200:
                answer = res.json().get("response", "").strip()
                return answer, f"Ollama ({self.model_name})"
            raise RuntimeError(f"Ollama returned HTTP {res.status_code}")
        except Exception as e:
            raise RuntimeError(f"Ollama error: {str(e)}")

ollama_client = OllamaClient()
