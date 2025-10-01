"""Online AI provider placeholder that simulates OpenAI responses."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .local_ollama import _summarize  # reuse deterministic summary


async def chat(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    context = context or {}
    intent = context.get("intent", "summary")
    result = context.get("result", {})
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "provider": "online",
            "intent": intent,
            "error": "OPENAI_API_KEY not configured",
            "message": "Set OPENAI_API_KEY to enable online summarisation.",
        }
    # In this offline-friendly implementation we return a deterministic summary.
    return {
        "provider": "online",
        "intent": intent,
        "message": _summarize(intent, result) + " (simulated OpenAI response)",
    }


__all__ = ["chat"]
