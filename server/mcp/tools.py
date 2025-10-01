"""MCP tool implementations that proxy to the FastAPI services."""
from __future__ import annotations

from typing import Any, Dict

from server.schemas import (
    ImpactRequest,
    MappingRequest,
    OptimizePlanRequest,
    ScoreRequest,
    SummaryRequest,
)
from server.services.impact import estimate_impact
from server.services.mapping import map_to_controls
from server.services.optimizer import generate_plan
from server.services.report import generate_summary
from server.services.scoring import score_compute


def score_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = ScoreRequest(**payload)
    response = score_compute(request)
    return response.model_dump(mode="json")


def plan_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = OptimizePlanRequest(**payload)
    response = generate_plan(request)
    return response.model_dump(mode="json")


def impact_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = ImpactRequest(**payload)
    response = estimate_impact(request)
    return response.model_dump(mode="json")


def map_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = MappingRequest(**payload)
    response = map_to_controls(request)
    return response.model_dump(mode="json")


def summary_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = SummaryRequest(**payload)
    response = generate_summary(request)
    return response.model_dump(mode="json")


def ingest_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "ingest not available via MCP in demo", "payload": payload}


def search_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "search not implemented", "payload": payload}


TOOL_REGISTRY: Dict[str, Any] = {
    "score": score_tool,
    "plan": plan_tool,
    "impact": impact_tool,
    "map": map_tool,
    "summary": summary_tool,
    "ingest": ingest_tool,
    "search": search_tool,
}


def call_tool(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_REGISTRY.get(name)
    if handler is None:
        return {"error": "unknown-tool", "tool": name, "payload": payload}
    return handler(payload)


__all__ = [
    "TOOL_REGISTRY",
    "score_tool",
    "plan_tool",
    "impact_tool",
    "map_tool",
    "summary_tool",
    "ingest_tool",
    "search_tool",
    "call_tool",
]
