"""Stubbed local AI provider."""
from __future__ import annotations

from typing import Any, Dict, Optional


async def chat(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a deterministic response representing a local provider."""
    return {
        "provider": "local",
        "prompt": prompt,
        "context": context or {},
        "message": "Local provider stub response.",
    }
