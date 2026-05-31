"""Async client for the local Ollama REST API."""

import httpx
from typing import Any
from app.config import settings


class OllamaClient:
    def __init__(self) -> None:
        self._base = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Send a generation request and return the full response text."""
        payload: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self._base}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json()["response"]

    async def chat(self, messages: list[dict], system: str | None = None) -> str:
        """Send a chat request (OpenAI-style messages list)."""
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self._base}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]
