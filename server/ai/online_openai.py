"""Stubbed online AI provider."""
from __future__ import annotations

from typing import Any, Dict, Optional


async def chat(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a deterministic response representing an online provider."""
    return {
        "provider": "online",
        "prompt": prompt,
        "context": context or {},
        "message": "Online provider stub response.",
    }
