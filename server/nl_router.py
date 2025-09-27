"""Natural language routing helpers for the Copilot experience."""

from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    """Represents the high-level intents supported by the router."""

    PLAN = "plan"
    COMPLIANCE = "compliance"
    NARRATIVE = "narrative"
    COPILOT = "copilot"


def infer_intent(message: str) -> Intent:
    """Basic keyword-based intent inference."""
    lowered = message.lower()
    if "plan" in lowered:
        return Intent.PLAN
    if "compliance" in lowered or "control" in lowered:
        return Intent.COMPLIANCE
    if "story" in lowered or "narrative" in lowered:
        return Intent.NARRATIVE
    return Intent.COPILOT


__all__ = [
    "Intent",
    "infer_intent",
]
