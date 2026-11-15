"""
SchoolGPT - LLM Client & Grounded Generator
Communicates with Ollama (Qwen3:4b) with robust fallback reasoning.
Enforces strict hallucination prevention and multilingual answers.
RSR Technologies
"""

import re
import time
import json
import requests
from typing import List, Dict, Any, Tuple
from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_LLM_MODEL,
    OLLAMA_FALLBACK_MODELS,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    INSUFFICIENT_INFO_MESSAGE,
    INSUFFICIENT_INFO_TRANSLATIONS,
    LANGUAGES
)

SYSTEM_PROMPT_TEMPLATE = """You are SchoolGPT, the official AI School Knowledge Assistant for RSR Technologies.
Your sole purpose is to provide clear, reliable, professional, and strictly accurate answers based ONLY on the provided official school context.

CRITICAL INSTRUCTIONS:
1. Answer the question using ONLY the provided School Context snippets below.
2. DO NOT invent, hallucinate, extrapolate, or assume school policies, fee amounts, deadlines, exam dates, or transportation rules.
3. If the provided context does NOT contain enough information to answer the question accurately, you MUST reply with this exact phrase:
   "I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."
4. Format your answer with clean markdown bullet points, bold highlights, and clear structure.
5. If the user's language is Kannada, provide the answer in natural Kannada while keeping proper school terms clear.
6. If the user's language is Hindi, provide the answer in clear formal Hindi.
7. Always remain courteous, authoritative, and helpful.
"""

class LLMService:
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model_name: str = OLLAMA_LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._cached_status = (False, [], "Not checked yet")
        self._last_check_time = 0
        self._cache_ttl_sec = 10.0

    def check_ollama_status(self) -> Tuple[bool, List[str], str]:
        """
        Checks if Ollama is running and lists installed models with caching.
        Returns (is_running, model_names, status_message).
        """
        now = time.time()
        if now - self._last_check_time < self._cache_ttl_sec and self._last_check_time > 0:
            return self._cached_status

        self._last_check_time = now
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=1.0)
            if res.status_code == 200:
                models = [m.get("name", "") for m in res.json().get("models", [])]
                self._cached_status = (True, models, "Ollama is running and connected.")
                return self._cached_status
            self._cached_status = (False, [], f"Ollama returned HTTP status {res.status_code}")
            return self._cached_status
        except requests.exceptions.ConnectionError:
            self._cached_status = (False, [], "Ollama is not running. Start Ollama with 'ollama serve' or check port 11434.")
            return self._cached_status
        except Exception as e:
            self._cached_status = (False, [], f"Error connecting to Ollama: {str(e)}")
            return self._cached_status

    def _build_context_prompt(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into numbered context blocks."""
        if not context_chunks:
            return "No school documents found."

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

        return "\n\n---\n\n".join(context_blocks)

    def _fallback_grounded_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> str:
        """
        Intelligent rule-based synthesis engine used when Ollama server is offline.
        Strictly grounds the answer on extracted chunks or returns the refusal phrase.
        """
        refusal_msg = INSUFFICIENT_INFO_TRANSLATIONS.get(language, INSUFFICIENT_INFO_MESSAGE)
        if not context_chunks:
            return refusal_msg

        # Filter meaningful query words
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
        
        # Distinguish core substantive keywords from generic school-wide terms
        core_keywords = [w for w in all_words if w not in generic_school_words]
        active_words = core_keywords if core_keywords else all_words

        if not active_words:
            return refusal_msg

        # Extract sentences from chunks with matching keywords (supporting prefix/stem matching)
        extracted_points = []
        primary_match_chunk = None

        # Build stem patterns for active words
        stem_patterns = []
        for w in active_words:
            stem = w[:-1] if (len(w) > 4 and w.endswith('s')) else w
            if len(stem) > 4:
                stem = stem[:4]
            stem_patterns.append(re.compile(r'\b' + re.escape(stem) + r'\w*', re.IGNORECASE))

        min_required = 2 if len(active_words) >= 2 else 1

        for chunk in context_chunks:
            text = chunk.get("text", "")
            sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if len(s.strip()) > 15]
            for s in sentences:
                matches = sum(1 for p in stem_patterns if p.search(s))
                # For multi-word substantive queries, require multiple keyword matches
                if matches >= min_required:
                    clean_s = s.replace("\n", " ").strip()
                    if clean_s not in extracted_points:
                        extracted_points.append(clean_s)
                        if primary_match_chunk is None:
                            primary_match_chunk = chunk

        # If no query keyword matched any sentence in the retrieved chunks, STRICT REFUSAL!
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

        english_answer = f"{ref_header}\n\n{bullet_points}\n\n*Note: Verified response extracted from institutional documents.*"

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

        return english_answer

    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en",
        conversation_history: List[Dict[str, str]] = None
    ) -> Tuple[str, str]:
        """
        Generates an answer using Ollama or grounded fallback.
        Returns (answer_text, model_used).
        """
        if not context_chunks:
            refusal = INSUFFICIENT_INFO_TRANSLATIONS.get(language, INSUFFICIENT_INFO_MESSAGE)
            return refusal, "SchoolGPT Policy Engine"

        is_running, installed_models, _ = self.check_ollama_status()

        target_model = self.model_name
        if is_running and installed_models:
            if target_model not in installed_models:
                matched = [m for m in installed_models if target_model.split(":")[0] in m]
                if matched:
                    target_model = matched[0]
                else:
                    target_model = installed_models[0]

        if not is_running:
            answer = self._fallback_grounded_answer(query, context_chunks, language)
            return answer, "SchoolGPT Grounded Engine (Offline Mode)"

        formatted_context = self._build_context_prompt(context_chunks)
        lang_instruction = ""
        if language == "kn":
            lang_instruction = "Respond in fluent, polite KANNADA (ಕನ್ನಡ)."
        elif language == "hi":
            lang_instruction = "Respond in clear, formal HINDI (हिन्दी)."

        user_prompt = f"""Language: {LANGUAGES.get(language, {}).get('name', 'English')}
{lang_instruction}

SCHOOL CONTEXT:
{formatted_context}

USER QUESTION:
{query}

ANSWER (Strictly grounded on the context above; if not found, use exact refusal phrase):"""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE}
        ]

        if conversation_history:
            for turn in conversation_history[-4:]:
                messages.append(turn)

        messages.append({"role": "user", "content": user_prompt})

        try:
            payload = {
                "model": target_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=20.0)
            if resp.status_code == 200:
                answer = resp.json().get("message", {}).get("content", "").strip()
                if answer:
                    return answer, f"Ollama ({target_model})"
        except Exception:
            pass

        fallback_ans = self._fallback_grounded_answer(query, context_chunks, language)
        return fallback_ans, "SchoolGPT Grounded Engine (Fallback)"

# Singleton LLM instance
llm_service = LLMService()
