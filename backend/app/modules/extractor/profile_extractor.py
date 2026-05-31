"""
Uses Ollama to extract structured school profile data from scraped text.
"""

import json
import re
from app.modules.extractor.ollama_client import OllamaClient
from app.config import settings

_SYSTEM_PROMPT = """
Jesteś asystentem analizującym strony szkół średnich. Twoim zadaniem jest
wyekstrahowanie ze strony szkoły ustrukturyzowanych informacji w formacie JSON.
Odpowiedź zwróć WYŁĄCZNIE jako JSON, bez żadnych dodatkowych wyjaśnień.
""".strip()

_EXTRACTION_PROMPT_TEMPLATE = """
Poniżej znajduje się tekst ze strony internetowej szkoły. Wyekstrahuj następujące informacje:

1. class_profiles – lista profili klas (np. matematyczno-fizyczny, humanistyczny, biologiczno-chemiczny)
   Dla każdego profilu: name, description (opcjonalnie), languages (lista języków obcych)
2. languages_offered – lista wszystkich języków obcych oferowanych przez szkołę
3. extracurricular_activities – lista kół zainteresowań / zajęć pozalekcyjnych
4. notable_achievements – sukcesy szkoły, wyniki olimpiad, rankingi
5. description_summary – krótkie podsumowanie szkoły (max 3 zdania)

Odpowiedź:
{{
  "class_profiles": [...],
  "languages_offered": [...],
  "extracurricular_activities": [...],
  "notable_achievements": [...],
  "description_summary": "..."
}}

Tekst strony:
---
{text}
---
"""


class ProfileExtractor:
    def __init__(self) -> None:
        self._ollama = OllamaClient()

    async def extract(self, plain_text: str) -> dict:
        """Extract structured school profile from plain text.
        Returns a dict with the extracted fields."""
        # Truncate to avoid overwhelming the context window (~6k tokens)
        truncated = plain_text[:8000]
        prompt = _EXTRACTION_PROMPT_TEMPLATE.format(text=truncated)

        raw_response = await self._ollama.generate(
            prompt=prompt, system=_SYSTEM_PROMPT
        )

        parsed = self._parse_json(raw_response)
        parsed["_raw_response"] = raw_response
        parsed["_model"] = settings.ollama_model
        return parsed

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract JSON block from LLM response, tolerating markdown fences."""
        # Try bare parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Extract first JSON object from the response
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {"parse_error": "Could not extract JSON", "_raw_response": text}
