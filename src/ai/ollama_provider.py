import json
import requests
from typing import Dict, Any


class OllamaTranslator:
    """Handles translation tasks locally via Ollama API with tag preservation."""

    def __init__(self, host: str = "http://localhost:11434", model_name: str = "llama3"):
        self.host = host.rstrip("/")
        self.model_name = model_name

    def _build_prompt(self, text_entries: Dict[str, str], target_language: str) -> str:
        return f"""
You are a game localization engine. Translate the following JSON object values into {target_language}.

RULES:
1. Do NOT translate variables, formatting tags, or code placeholders (e.g., {{0}}, <color=red>, \\n).
2. Return strictly valid JSON containing only the key-value pairs.

Input JSON:
{json.dumps(text_entries, ensure_ascii=False, indent=2)}
"""

    def translate_batch(
        self, text_entries: Dict[str, str], target_language: str = "Arabic"
    ) -> Dict[str, str]:
        if not text_entries:
            return {}

        prompt = self._build_prompt(text_entries, target_language)

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json().get("response", "{}")
                return json.loads(result)
            else:
                print(f"Ollama request failed with status: {response.status_code}")
                return text_entries
        except Exception as e:
            print(f"Error connecting to local Ollama server: {e}")
            return text_entries