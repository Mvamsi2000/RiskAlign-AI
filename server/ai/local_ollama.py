"""Local Ollama AI provider implementation."""
from __future__ import annotations

import os
from typing import Any, List, Mapping

import httpx

from .provider import AIProvider, AIProviderError, Message


class LocalOllamaProvider(AIProvider):
    """Interact with a locally hosted Ollama API."""

    def __init__(self, *, base_url: str | None = None, model: str | None = None, timeout: float = 30.0) -> None:
        self._base_url = base_url or os.getenv("AI_LOCAL_BASE_URL", "http://127.0.0.1:11434")
        self._model = model or os.getenv("AI_LOCAL_MODEL", "llama3:8b")
        self._timeout = timeout

    def name(self) -> str:
        return "Local (Ollama)"

    def chat(self, messages: List[Message], **kwargs: Any) -> str:
        payload: Mapping[str, Any] = {
            "model": self._model,
            "messages": list(messages),
            "stream": False,
        }
        if kwargs:
            payload = {**payload, **kwargs}

        url = f"{self._base_url.rstrip('/')}/api/chat"
        try:
            response = httpx.post(url, json=payload, timeout=self._timeout)
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise AIProviderError(f"Failed to reach local Ollama service: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise AIProviderError(
                f"Local Ollama returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc

        data = response.json()
        message = data.get("message") or {}
        content = message.get("content") or data.get("response")
        if not content:
            raise AIProviderError("Local Ollama response did not contain message content.")
        return str(content)
