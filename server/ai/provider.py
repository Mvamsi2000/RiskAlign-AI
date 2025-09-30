"""AI provider selection helpers."""
from __future__ import annotations

import os
from typing import Any, Awaitable, Callable, Dict, Optional

from . import local_ollama, online_openai

ProviderFunc = Callable[[str, Optional[Dict[str, Any]]], Awaitable[Dict[str, Any]]]

_PROVIDER_DEFAULT = os.getenv("AI_PROVIDER_DEFAULT", "local").lower()
_PROVIDERS: Dict[str, ProviderFunc] = {
    "local": local_ollama.chat,
    "online": online_openai.chat,
}


def resolve_provider(name: Optional[str]) -> ProviderFunc:
    """Resolve an AI provider function by name."""
    key = (name or _PROVIDER_DEFAULT).lower()
    return _PROVIDERS.get(key, local_ollama.chat)


async def dispatch(prompt: str, provider: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Dispatch a chat request to the resolved provider."""
    handler = resolve_provider(provider)
    return await handler(prompt, context)


__all__ = ["dispatch", "resolve_provider"]
