"""Simple intent resolution for the NL copilot."""
from __future__ import annotations

from typing import Dict

from server.mcp import tools

_KEYWORD_INTENT = {
    "ingest": "ingest",
    "upload": "ingest",
    "score": "score",
    "plan": "plan",
    "impact": "impact",
    "map": "map",
    "summary": "summary",
    "search": "search",
}


def resolve_intent(prompt: str) -> Dict[str, str]:
    """Return the chosen intent and tool name for a natural-language prompt."""
    lowered = prompt.lower()
    for keyword, intent in _KEYWORD_INTENT.items():
        if keyword in lowered:
            return {"intent": intent, "tool": intent}
    return {"intent": "summary", "tool": "summary"}


def execute_intent(prompt: str, payload: Dict[str, object] | None = None) -> Dict[str, object]:
    """Resolve an intent and execute the associated MCP tool."""
    resolution = resolve_intent(prompt)
    tool_name = resolution["tool"]
    result = tools.call_tool(tool_name, payload or {})
    return {**resolution, "result": result}


__all__ = ["resolve_intent", "execute_intent"]
