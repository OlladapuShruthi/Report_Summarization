from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.analysis.llm.groq_client import GroqClient
from app.analysis.parser.validator import MedicalJSONValidator


class LLMStructurer:
    """Strict LLM fallback for documents deterministic extraction cannot structure."""

    def __init__(self, client: Optional[GroqClient] = None):
        self.client = client or GroqClient()
        self.validator = MedicalJSONValidator()

    @property
    def enabled(self) -> bool:
        return self.client.enabled

    def extract(self, text: str, report_type_hint: str = "UNKNOWN") -> Dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("LLM structured extraction is not configured")

        response = self.client.chat_completion_sync(self._build_prompt(text, report_type_hint), temperature=0.0)
        payload = self._parse_json_response(response)
        validated = self.validator.validate(payload)
        validated.setdefault("parser_metadata", {})
        validated["parser_metadata"].update(
            {
                "llm_used": True,
                "llm_model": self.client.model,
                "llm_structuring": True,
            }
        )
        return validated

    @staticmethod
    def _build_prompt(text: str, report_type_hint: str) -> list[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "Extract only explicitly stated medical facts from the source text. "
                    "Return one JSON object and no markdown or explanation. Never infer or diagnose. "
                    "Use schema_version 1.0, report_type, patient_metadata, lab_results, "
                    "narrative_impressions, confidence, and parser_metadata. "
                    "Every lab result must include a numeric value and preserve its stated unit "
                    "and reference range."
                ),
            },
            {
                "role": "user",
                "content": f"Report type hint: {report_type_hint}\nSource text:\n{text}",
            },
        ]

    @staticmethod
    def _parse_json_response(response: str) -> Dict[str, Any]:
        content = (response or "").strip()
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3].strip()
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM structured extraction returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("LLM structured extraction must return a JSON object")
        return payload
