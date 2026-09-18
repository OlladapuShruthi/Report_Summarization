from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class GroqClient:
    PROVIDER_DEFAULTS = {
        "gemini": (
            "https://generativelanguage.googleapis.com/v1beta/openai/",
            "gemini-3.8-flash",
        ),
        "xai": ("https://api.x.ai/v1", "grok-4.6"),
        "groq": ("https://api.groq.com/openai/v1", "qwen/qwen3.6-27b"),
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        provider = settings.LLM_PROVIDER.strip().lower()
        provider_base_url, provider_model = self.PROVIDER_DEFAULTS.get(provider, (settings.GROQ_BASE_URL, settings.GROQ_MODEL))
        self.api_key = api_key or settings.LLM_API_KEY or settings.GROQ_API_KEY
        self.base_url = (base_url or settings.LLM_BASE_URL or provider_base_url).rstrip("/")
        self.model = model or settings.LLM_MODEL or provider_model
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        if not self.enabled:
            raise RuntimeError("LLM API key is not configured")

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("Groq chat completion returned no choices")

        message = choices[0].get("message") or {}
        content = message.get("content") or ""
        return content.strip()

    def chat_completion_sync(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        if not self.enabled:
            raise RuntimeError("LLM API key is not configured")

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("Groq chat completion returned no choices")
        return str((choices[0].get("message") or {}).get("content") or "").strip()
