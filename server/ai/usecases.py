"""High-level AI helpers for business use-cases."""
from __future__ import annotations

import json
import os
from typing import Any, Mapping, Optional

from fastapi import Request

from .provider import AIProviderError
from .resolve import ProviderResolutionError, resolve_provider


def _ai_feature_enabled(env_var: str) -> bool:
    return os.getenv(env_var, "1").strip() not in {"0", "false", "False"}


def generate_summary_narrative(
    request: Request | None,
    *,
    tenant_config: Mapping[str, Any] | None = None,
    namespace: str | None = None,
    context: Mapping[str, Any],
) -> Optional[str]:
    """Generate a summary narrative using the configured AI provider."""

    if not _ai_feature_enabled("AI_NARRATIVE_ENABLED"):
        return None
    if request is None and namespace is None:
        # Cannot resolve provider without any routing context.
        return None

    try:
        _, provider = resolve_provider(request, tenant_config, namespace=namespace)
    except (ProviderResolutionError, AIProviderError):
        return None

    messages = [
        {
            "role": "system",
            "content": (
                "You are a cybersecurity analyst. Summarise remediation and risk trends for executives. "
                "Keep it under 150 words and focus on prioritisation rationale."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(context, ensure_ascii=False),
        },
    ]

    try:
        narrative = provider.chat(messages, max_tokens=400)
    except AIProviderError:
        return None

    return narrative.strip() or None


__all__ = ["generate_summary_narrative"]
