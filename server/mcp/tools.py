"""Deterministic MCP tool stubs."""
from __future__ import annotations

from typing import Any, Callable, Dict

ToolFunction = Callable[[Dict[str, Any]], Dict[str, Any]]


def _basic_response(tool: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"tool": tool, "received": payload}


def ingest_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("ingest_tool", payload)


def score_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("score_tool", payload)


def plan_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("plan_tool", payload)


def impact_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("impact_tool", payload)


def map_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("map_tool", payload)


def summary_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("summary_tool", payload)


def search_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _basic_response("search_tool", payload)


TOOL_REGISTRY: Dict[str, ToolFunction] = {
    "ingest": ingest_tool,
    "score": score_tool,
    "plan": plan_tool,
    "impact": impact_tool,
    "map": map_tool,
    "summary": summary_tool,
    "search": search_tool,
}


def call_tool(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke a registered MCP tool by name."""
    handler = TOOL_REGISTRY.get(name)
    if handler is None:
        return {"tool": name, "error": "unknown-tool", "received": payload}
    return handler(payload)


__all__ = [
    "TOOL_REGISTRY",
    "ingest_tool",
    "score_tool",
    "plan_tool",
    "impact_tool",
    "map_tool",
    "summary_tool",
    "search_tool",
    "call_tool",
]
