"""
Google Gemini API Client for SchoolGPT
Provides high-speed, grounded generation using Gemini 1.5 Flash / Gemini Pro.
RSR Technologies
"""

import os
from typing import List, Dict, Any, Tuple
from backend.config import settings

SYSTEM_PROMPT = """You are SchoolGPT, the official AI School Knowledge Assistant for RSR Technologies.
Your sole purpose is to provide clear, reliable, professional, and strictly accurate answers based ONLY on the provided official school context.

CRITICAL INSTRUCTIONS:
1. Answer the question using ONLY the provided School Context snippets below.
2. DO NOT invent, hallucinate, extrapolate, or assume school policies, fee amounts, deadlines, exam dates, or transportation rules.
3. If the provided context does NOT contain enough information to answer the question accurately, you MUST reply with this exact phrase:
   "I could not find reliable information about this question in the school's uploaded documents. Please contact the school administration."
4. If the requested language is Kannada, provide the answer in natural Kannada. If the required information is not found, reply:
   "ಶಾಲೆಯ ಅಧಿಕೃತ ದಾಖಲೆಗಳಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಶಾಲಾ ಆಡಳಿತವನ್ನು ಸಂಪರ್ಕಿಸಿ."
5. If the requested language is Hindi, provide the answer in clear formal Hindi. If the required information is not found, reply:
   "स्कूल के आधिकारिक दस्तावेजों में इस प्रश्न के बारे में विश्वसनीय जानकारी नहीं मिली। कृपया स्कूल प्रशासन से संपर्क करें।"
6. Format your answer with clean markdown bullet points and bold highlights.
"""

class GeminiClient:
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT
            )
        except Exception as e:
            print(f"Notice: Gemini init error: {e}")
            self._client = None

    def is_available(self) -> bool:
        return self._client is not None and bool(self.api_key)

    def generate(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> Tuple[str, str]:
        """
        Generates grounded answer using Google Gemini.
        Returns (answer_text, model_name).
        """
        if not self.is_available():
            raise RuntimeError("Gemini API key is not configured.")

        # Build context prompt
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
        prompt = f"""Language requested: {language}

Official School Context Documents:
{context_str}

User Question:
{query}

Answer strictly using the documents above:"""

        try:
            response = self._client.generate_content(prompt)
            answer = response.text.strip()
            return answer, f"Google Gemini ({self.model_name})"
        except Exception as e:
            raise RuntimeError(f"Gemini generation error: {str(e)}")

gemini_client = GeminiClient()
