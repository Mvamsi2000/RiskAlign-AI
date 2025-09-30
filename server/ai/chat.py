"""Chat orchestration helper for the NL router."""
from __future__ import annotations

from typing import Dict, Optional

from . import provider, resolve


async def handle_chat(prompt: str, provider_name: Optional[str] = None, payload: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Execute an intent resolution followed by a provider dispatch."""
    resolution = resolve.execute_intent(prompt, payload)
    provider_response = await provider.dispatch(prompt, provider_name, context=resolution)
    return {
        "intent": resolution["intent"],
        "tool_called": resolution["tool"],
        "result": resolution["result"],
        "provider_state": provider_response,
    }


__all__ = ["handle_chat"]
