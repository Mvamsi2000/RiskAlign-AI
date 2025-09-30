"""Shared API-facing schemas."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .finding import CanonicalFinding


class ScoringWeights(BaseModel):
    """Relative weights applied to individual scoring dimensions."""

    model_config = ConfigDict(extra="forbid")

    cvss: float = Field(0.6, ge=0, description="Weight applied to CVSS scores")
    epss: float = Field(0.3, ge=0, description="Weight applied to EPSS probabilities")
    kev: float = Field(0.1, ge=0, description="Weight applied when a finding is on the KEV list")
    context: float = Field(0.0, ge=0, description="Custom context multiplier for future extensions")


class ScoringConfig(BaseModel):
    """Configuration payload accepted by the scoring engine."""

    model_config = ConfigDict(extra="ignore")

    max_score: float = Field(10.0, gt=0, description="Maximum risk score that may be returned")
    risk_tolerance: float = Field(7.5, ge=0, le=10, description="Threshold representing acceptable risk")
    weights: ScoringWeights = Field(default_factory=ScoringWeights, description="Weights for scoring dimensions")


class IngestResponse(BaseModel):
    """Response returned by the ingestion endpoint."""

    model_config = ConfigDict(extra="ignore")

    count: int = Field(..., ge=0, description="Total number of findings detected in the artifact")
    sample: List[CanonicalFinding] = Field(default_factory=list, description="Sample findings extracted from the artifact")


class ScoreFinding(CanonicalFinding):
    """Canonical finding augmented with scoring metadata."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    score: float = Field(0.0, ge=0, le=10, description="Calculated risk score")
    bucket: str = Field("low", description="Risk bucket label")
    effort_hours: float = Field(0.0, ge=0, description="Estimated effort in hours")


class ScoreSummary(BaseModel):
    """Aggregated scoring summary."""

    model_config = ConfigDict(extra="ignore")

    total_findings: int = Field(0, ge=0, description="Total findings considered")
    average_score: float = Field(0.0, ge=0, le=10, description="Average risk score")
    critical: int = Field(0, ge=0, description="Number of critical findings")
    high: int = Field(0, ge=0, description="Number of high findings")
    medium: int = Field(0, ge=0, description="Number of medium findings")
    low: int = Field(0, ge=0, description="Number of low findings")
    total_effort_hours: float = Field(0.0, ge=0, description="Total estimated effort in hours")


class ScoreRequest(BaseModel):
    """Request body for score computation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[CanonicalFinding] = Field(default_factory=list, description="Findings to be scored")
    config: Optional[ScoringConfig] = Field(None, description="Overrides for scoring configuration")


class ScoreResponse(BaseModel):
    """Response body for score computation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Scored findings")
    summary: ScoreSummary = Field(default_factory=ScoreSummary, description="Aggregated scoring summary")


class Wave(BaseModel):
    """Represents a remediation wave produced by the optimizer."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Human readable label for the wave")
    order: int = Field(..., ge=0, description="Zero-based index of the wave")
    capacity_hours: float = Field(..., ge=0, description="Effort budget assigned to the wave")
    findings: List[str] = Field(default_factory=list, description="Identifiers of findings scheduled in the wave")
    total_risk_reduction: float = Field(0.0, ge=0, description="Aggregate risk reduction achieved by the wave")
    estimated_effort_hours: float = Field(0.0, ge=0, description="Estimated effort to complete the wave")


class OptimizeRequest(BaseModel):
    """Request payload for the optimizer."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Findings available for planning")
    budget_hours: Optional[float] = Field(None, ge=0, description="Total effort budget across all waves")
    wave_size: Optional[int] = Field(None, ge=1, description="Optional number of findings per wave")


class OptimizeResponse(BaseModel):
    """Response payload from the optimizer."""

    model_config = ConfigDict(extra="ignore")

    waves: List[Wave] = Field(default_factory=list, description="Generated remediation waves")
    unassigned: List[str] = Field(default_factory=list, description="Identifiers of findings not placed in any wave")


class ImpactRequest(BaseModel):
    """Request payload for impact estimation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Scored findings used for impact analysis")
    waves: List[Wave] = Field(default_factory=list, description="Planned remediation waves")


class ImpactPoint(BaseModel):
    """Data point on the risk reduction curve."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., description="Label for the curve point")
    risk_reduction: float = Field(..., ge=0, description="Cumulative risk reduction percentage")


class ImpactResponse(BaseModel):
    """Response payload for impact estimation."""

    model_config = ConfigDict(extra="ignore")

    readiness_pct: float = Field(0.0, ge=0, le=100, description="Overall readiness percentage")
    residual_risk: float = Field(100.0, ge=0, description="Residual risk percentage")
    risk_saved_curve: List[ImpactPoint] = Field(default_factory=list, description="Risk reduction curve data points")


class MappingRequest(BaseModel):
    """Request payload for controls mapping."""

    model_config = ConfigDict(extra="ignore")

    findings: List[CanonicalFinding] = Field(default_factory=list, description="Findings to map to controls")
    framework: str = Field("CIS", description="Compliance framework identifier")


class MappingRow(BaseModel):
    """Row representing a control mapping."""

    model_config = ConfigDict(extra="ignore")

    control_id: str = Field(..., description="Control identifier")
    title: str = Field(..., description="Control title")
    description: str = Field("", description="Control description")
    related_findings: List[str] = Field(default_factory=list, description="Identifiers of findings mapped to the control")


class MappingResponse(BaseModel):
    """Response payload for controls mapping."""

    model_config = ConfigDict(extra="ignore")

    framework: str = Field(..., description="Framework identifier")
    coverage_pct: float = Field(0.0, ge=0, le=100, description="Coverage percentage")
    rows: List[MappingRow] = Field(default_factory=list, description="Control mapping rows")


class SummaryRequest(BaseModel):
    """Request payload for summary generation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Findings included in the summary")
    waves: List[Wave] = Field(default_factory=list, description="Remediation plan included in the summary")
    notes: Optional[str] = Field(None, description="Optional analyst notes")


class SummaryResponse(BaseModel):
    """Response payload for summary generation."""

    model_config = ConfigDict(extra="ignore")

    report_url: str = Field(..., description="Relative URL where the rendered report can be fetched")


class NLQueryRequest(BaseModel):
    """Request payload for the natural language query endpoint."""

    model_config = ConfigDict(extra="ignore")

    query: str = Field(..., description="Natural language prompt")
    context: Dict[str, Any] = Field(default_factory=dict, description="Optional context to pass to the intent resolver")


class NLQueryResponse(BaseModel):
    """Response payload for the natural language query endpoint."""

    model_config = ConfigDict(extra="ignore")

    intent: str = Field(..., description="Resolved intent")
    tool_called: str = Field(..., description="Tool that was executed")
    result: Dict[str, Any] = Field(default_factory=dict, description="Result returned by the tool")
    provider_state: Dict[str, Any] = Field(default_factory=dict, description="Additional provider metadata")


__all__ = [
    "CanonicalFinding",
    "ScoringConfig",
    "ScoringWeights",
    "IngestResponse",
    "ScoreFinding",
    "ScoreSummary",
    "ScoreRequest",
    "ScoreResponse",
    "Wave",
    "OptimizeRequest",
    "OptimizeResponse",
    "ImpactRequest",
    "ImpactResponse",
    "ImpactPoint",
    "MappingRequest",
    "MappingResponse",
    "MappingRow",
    "SummaryRequest",
    "SummaryResponse",
    "NLQueryRequest",
    "NLQueryResponse",
]
