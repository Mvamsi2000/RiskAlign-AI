"""Helpers to resolve the active AI provider per request."""
from __future__ import annotations

import json
import os
from typing import Mapping, MutableMapping, Tuple

from fastapi import Request

from .local_ollama import LocalOllamaProvider
from .online_openai import OnlineOpenAIProvider
from .provider import AIProvider, AIProviderError
from ..core.tenancy import namespace_ai_config_path

_PROVIDER_IDS = {"local", "online"}


class ProviderResolutionError(RuntimeError):
    """Raised when the provider cannot be determined."""


def _load_namespace_ai_config(namespace: str) -> MutableMapping[str, str]:
    config_path = namespace_ai_config_path(namespace)
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def resolve_provider(
    request: Request | None,
    tenant_cfg: Mapping[str, str] | None = None,
    *,
    namespace: str | None = None,
) -> Tuple[str, AIProvider]:
    """Resolve the provider id and instance for this request."""

    header_value = None
    if request is not None:
        header_value = request.headers.get("X-AI-Provider")
    candidate = (header_value or "").strip().lower()

    if candidate not in _PROVIDER_IDS:
        if tenant_cfg and isinstance(tenant_cfg, Mapping):
            candidate = str(tenant_cfg.get("ai_provider", "")).strip().lower()
        if candidate not in _PROVIDER_IDS and namespace:
            stored = _load_namespace_ai_config(namespace)
            candidate = str(stored.get("ai_provider", "")).strip().lower()
        if candidate not in _PROVIDER_IDS:
            candidate = os.getenv("AI_PROVIDER_DEFAULT", "local").strip().lower()

    if candidate not in _PROVIDER_IDS:
        raise ProviderResolutionError(f"Unsupported AI provider '{candidate}'.")

    if candidate == "online":
        provider: AIProvider = OnlineOpenAIProvider()
    else:
        provider = LocalOllamaProvider()
    return candidate, provider


__all__ = ["resolve_provider", "ProviderResolutionError", "AIProvider", "AIProviderError"]
