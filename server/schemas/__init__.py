"""Pydantic schemas used across the RiskAlign API."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Type

from pydantic import BaseModel

from .api import (  # noqa: F401
    AssetContext,
    Contribution,
    ControlMapping,
    FeedbackRequest,
    FeedbackResponse,
    Finding,
    ImpactEstimateRequest,
    ImpactEstimateResponse,
    MapControlsRequest,
    MapControlsResponse,
    NLQueryRequest,
    NLQueryResponse,
    OptimizePlanRequest,
    OptimizePlanResponse,
    RemediationWave,
    ScoreComputeRequest,
    ScoreComputeResponse,
    ScoreSummary,
    ScoredFinding,
    SummaryGenerateRequest,
    SummaryGenerateResponse,
    WaveItem,
)
from .envelope import MCPEnvelope  # noqa: F401
from .finding import CanonicalAsset, CanonicalFinding, CanonicalSignals  # noqa: F401

__all__ = [
    "AssetContext",
    "Contribution",
    "ControlMapping",
    "FeedbackRequest",
    "FeedbackResponse",
    "Finding",
    "ImpactEstimateRequest",
    "ImpactEstimateResponse",
    "MapControlsRequest",
    "MapControlsResponse",
    "NLQueryRequest",
    "NLQueryResponse",
    "OptimizePlanRequest",
    "OptimizePlanResponse",
    "RemediationWave",
    "ScoreComputeRequest",
    "ScoreComputeResponse",
    "ScoreSummary",
    "ScoredFinding",
    "SummaryGenerateRequest",
    "SummaryGenerateResponse",
    "WaveItem",
    "CanonicalAsset",
    "CanonicalSignals",
    "CanonicalFinding",
    "MCPEnvelope",
]


def export_json_schemas(target_dir: Path | None = None) -> Dict[str, Path]:
    """Write JSON schema files for key public models."""

    schema_dir = target_dir or Path(__file__).resolve().parent / "json"
    schema_dir.mkdir(parents=True, exist_ok=True)

    models: Dict[str, Type[BaseModel]] = {
        "canonical_finding.json": CanonicalFinding,
        "mcp_envelope.json": MCPEnvelope,
    }

    written: Dict[str, Path] = {}
    for filename, model in models.items():
        path = schema_dir / filename
        payload = model.model_json_schema(mode="serialization")
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        written[filename] = path
    return written


__all__.append("export_json_schemas")
