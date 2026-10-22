import json
import os
from typing import Dict, Any, List
from google import genai
from google.genai import types


class GeminiTranslator:
    """Handles translation tasks using Google GenAI SDK with tag preservation rules."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)

    def _build_system_instruction(self, target_language: str) -> str:
        return f"""
You are an expert game localization engine translating game texts into {target_language}.

CRITICAL RULES:
1. Do NOT modify or translate variable placeholders, HTML tags, or formatting codes (e.g., {{0}}, {{name}}, <color=red>, \\n, %s).
2. Maintain original context and tone suited for video games.
3. Return the translations strictly in valid JSON format matching the original input structure.
"""

    def translate_batch(
        self, text_entries: Dict[str, str], target_language: str = "Arabic"
    ) -> Dict[str, str]:
        """Translates a dictionary of key-value text entries while preserving tags."""
        if not text_entries:
            return {}

        prompt_content = json.dumps(text_entries, ensure_ascii=False, indent=2)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_content,
                config=types.GenerateContentConfig(
                    system_instruction=self._build_system_instruction(
                        target_language
                    ),
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )

            translated_data = json.loads(response.text)
            return translated_data
        except Exception as e:
            print(f"Error during Gemini translation: {e}")
            return text_entries