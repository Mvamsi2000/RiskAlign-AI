"""Chat orchestration helper for the NL router."""
from __future__ import annotations

from typing import Dict, Optional

from . import provider, resolve


async def handle_chat(
    prompt: str,
    provider_name: Optional[str] = None,
    payload: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    """Execute an intent resolution followed by a provider dispatch."""

    resolution = resolve.execute_intent(prompt, payload or {})
    provider_response = await provider.dispatch(prompt, provider_name, context=resolution)
    message = provider_response.get("message") or "Request processed successfully."

    details = {
        "matched_keywords": resolution.get("matched_keywords", []),
        "confidence": resolution.get("confidence", 0.0),
        "endpoint": resolution.get("endpoint"),
        "provider": provider_response.get("provider"),
        "provider_error": provider_response.get("error"),
    }
    return {
        "intent": resolution["intent"],
        "response": message,
        "details": details,
    }


__all__ = ["handle_chat"]
