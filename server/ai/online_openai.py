"""OpenAI-compatible online AI provider."""
from __future__ import annotations

import os
from typing import Any, List, Mapping

import httpx

from .provider import AIProvider, AIProviderError, Message


class OnlineOpenAIProvider(AIProvider):
    """Call the OpenAI chat completions endpoint."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url or os.getenv("AI_ONLINE_BASE_URL", "https://api.openai.com/v1")
        self._model = model or os.getenv("AI_ONLINE_MODEL", "gpt-4o-mini")
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._timeout = timeout

    def name(self) -> str:
        return "Online (OpenAI)"

    def chat(self, messages: List[Message], **kwargs: Any) -> str:
        if not self._api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured for online AI usage.")

        payload: Mapping[str, Any] = {
            "model": self._model,
            "messages": list(messages),
            "temperature": kwargs.get("temperature", 0.2),
        }
        if "max_tokens" in kwargs:
            payload = {**payload, "max_tokens": kwargs["max_tokens"]}

        url = f"{self._base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=self._timeout)
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise AIProviderError(f"Failed to reach OpenAI service: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise AIProviderError(
                f"OpenAI returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc

        data = response.json()
        choices = data.get("choices")
        if not choices:
            raise AIProviderError("OpenAI response did not include choices.")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise AIProviderError("OpenAI response did not include message content.")
        return str(content)
