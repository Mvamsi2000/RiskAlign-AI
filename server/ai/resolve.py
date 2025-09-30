"""Intent resolution for the NL copilot."""
from __future__ import annotations

from typing import Dict, List

from server.mcp import tools

_INTENTS: List[Dict[str, object]] = [
    {
        "intent": "ingest",
        "tool": "ingest",
        "keywords": ["ingest", "upload", "parse"],
        "endpoint": "/api/ingest/upload",
    },
    {
        "intent": "score",
        "tool": "score",
        "keywords": ["score", "prioritize", "risk"],
        "endpoint": "/api/score/compute",
    },
    {
        "intent": "plan",
        "tool": "plan",
        "keywords": ["plan", "wave", "quick win", "optimize"],
        "endpoint": "/api/optimize/plan",
    },
    {
        "intent": "impact",
        "tool": "impact",
        "keywords": ["impact", "readiness", "curve"],
        "endpoint": "/api/impact/estimate",
    },
    {
        "intent": "map",
        "tool": "map",
        "keywords": ["map", "control", "compliance", "cis"],
        "endpoint": "/api/map/controls",
    },
    {
        "intent": "summary",
        "tool": "summary",
        "keywords": ["summary", "report", "executive"],
        "endpoint": "/api/summary/generate",
    },
]

_DEFAULT_INTENT = {
    "intent": "summary",
    "tool": "summary",
    "keywords": [],
    "endpoint": "/api/summary/generate",
}


def resolve_intent(prompt: str) -> Dict[str, object]:
    """Return the chosen intent and metadata for a natural-language prompt."""

    lowered = prompt.lower()
    for candidate in _INTENTS:
        matched = [keyword for keyword in candidate["keywords"] if keyword in lowered]
        if matched:
            return {**candidate, "matched_keywords": matched}
    return {**_DEFAULT_INTENT, "matched_keywords": []}


def execute_intent(prompt: str, payload: Dict[str, object] | None = None) -> Dict[str, object]:
    """Resolve an intent and execute the associated MCP tool."""

    resolution = resolve_intent(prompt)
    result = tools.call_tool(resolution["tool"], payload or {})
    matched_keywords = resolution.get("matched_keywords", [])
    confidence = min(1.0, 0.4 + 0.15 * len(matched_keywords)) if matched_keywords else 0.35
    return {
        "intent": resolution["intent"],
        "tool": resolution["tool"],
        "endpoint": resolution.get("endpoint"),
        "matched_keywords": matched_keywords,
        "confidence": round(confidence, 2),
        "result": result,
    }


__all__ = ["resolve_intent", "execute_intent"]
