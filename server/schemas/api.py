"""Shared API-facing schemas for the RiskAlign-AI platform."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .finding import AssetContext, CanonicalFinding


class IngestResponse(BaseModel):
    """Response returned by the ingestion endpoint."""

    model_config = ConfigDict(extra="ignore")

    count: int = Field(..., ge=0, description="Total number of findings detected in the artifact")
    sample: List[CanonicalFinding] = Field(
        default_factory=list, description="Sample findings extracted from the artifact"
    )
    envelope: Dict[str, Any] = Field(
        default_factory=dict,
        description="Serialized MCP envelope representing the normalized payload",
    )


class ScoringWeights(BaseModel):
    """Relative weights applied to individual scoring dimensions."""

    model_config = ConfigDict(extra="forbid")

    cvss: float = Field(0.6, ge=0, description="Weight applied to CVSS scores")
    epss: float = Field(0.25, ge=0, description="Weight applied to EPSS probabilities")
    kev: float = Field(0.1, ge=0, description="Weight applied when a finding is on the KEV list")
    context: float = Field(0.05, ge=0, description="Weight applied to contextual multipliers")


class ScoringConfig(BaseModel):
    """Configuration payload accepted by the scoring engine."""

    model_config = ConfigDict(extra="ignore")

    max_score: float = Field(10.0, gt=0, description="Maximum risk score that may be returned")
    risk_tolerance: float = Field(
        7.5, ge=0, le=10, description="Threshold representing acceptable residual risk"
    )
    weights: ScoringWeights = Field(
        default_factory=ScoringWeights, description="Weights for scoring dimensions"
    )


class ScoreComponents(BaseModel):
    """Breakdown of component contributions that form the final score."""

    model_config = ConfigDict(extra="ignore")

    cvss: float = Field(0.0, ge=0, description="Contribution from the CVSS base score")
    epss: float = Field(0.0, ge=0, description="Contribution from the EPSS probability")
    mvi: float = Field(0.0, ge=0, description="Contribution from vendor maturity index")
    kev: float = Field(0.0, ge=0, description="Contribution from KEV designation")
    context: float = Field(0.0, ge=0, description="Contribution from contextual multipliers")


class ScoreFinding(CanonicalFinding):
    """Canonical finding augmented with scoring metadata."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    score: float = Field(0.0, ge=0, le=10, description="Calculated risk score")
    priority: str = Field("Low", description="Priority bucket label")
    effort_hours: float = Field(0.0, ge=0, description="Estimated effort in hours")
    risk_saved: float = Field(0.0, ge=0, description="Estimated risk reduction if remediated")
    components: ScoreComponents = Field(
        default_factory=ScoreComponents, description="Score component contributions"
    )
    context_multiplier: float = Field(
        1.0, ge=0, description="Multiplier applied based on asset context and tags"
    )


class ScoreTotals(BaseModel):
    """Aggregated scoring summary."""

    model_config = ConfigDict(extra="ignore")

    count: int = Field(0, ge=0, description="Total findings considered")
    total_score: float = Field(0.0, ge=0, description="Sum of all scores")
    average_score: float = Field(0.0, ge=0, le=10, description="Average risk score")
    total_effort_hours: float = Field(0.0, ge=0, description="Total estimated effort in hours")
    by_priority: Dict[str, int] = Field(
        default_factory=dict, description="Count of findings grouped by priority"
    )


class ScoreRequest(BaseModel):
    """Request body for score computation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[CanonicalFinding] = Field(default_factory=list, description="Findings to be scored")
    config: Optional[ScoringConfig] = Field(None, description="Overrides for scoring configuration")


class ScoreComputeResponse(BaseModel):
    """Response body for score computation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Scored findings")
    totals: ScoreTotals = Field(default_factory=ScoreTotals, description="Aggregated scoring summary")


class PlanItem(BaseModel):
    """Represents an individual remediation action within a wave."""

    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = Field(None, description="Identifier of the underlying finding")
    title: Optional[str] = Field(None, description="Title of the finding")
    priority: str = Field(..., description="Priority bucket of the finding")
    effort_hours: float = Field(..., ge=0, description="Effort required to remediate")
    score: float = Field(..., ge=0, le=10, description="Risk score of the finding")
    risk_saved: float = Field(..., ge=0, description="Estimated risk reduction from completion")


class RemediationWave(BaseModel):
    """Represents a remediation wave produced by the optimizer."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Human readable label for the wave")
    total_hours: float = Field(..., ge=0, description="Total effort hours within the wave")
    risk_saved: float = Field(..., ge=0, description="Total risk reduction delivered by the wave")
    items: List[PlanItem] = Field(default_factory=list, description="Ordered list of planned items")


class PlanTotals(BaseModel):
    """Aggregated view of the remediation plan."""

    model_config = ConfigDict(extra="ignore")

    waves: int = Field(0, ge=0, description="Number of waves")
    total_hours: float = Field(0.0, ge=0, description="Total effort across all waves")
    total_risk_saved: float = Field(0.0, ge=0, description="Total risk reduction across all waves")


class OptimizePlanRequest(BaseModel):
    """Request payload for the optimizer."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Findings available for planning")
    max_hours_per_wave: Optional[float] = Field(
        16.0, ge=1.0, description="Maximum effort capacity for a single wave"
    )
    minimum_waves: int = Field(1, ge=1, description="Minimum number of waves to return")


class OptimizePlanResponse(BaseModel):
    """Response payload from the optimizer."""

    model_config = ConfigDict(extra="ignore")

    waves: List[RemediationWave] = Field(default_factory=list, description="Generated remediation waves")
    totals: PlanTotals = Field(default_factory=PlanTotals, description="Aggregate metrics for the plan")
    unassigned: List[str] = Field(default_factory=list, description="Identifiers of findings not placed in any wave")


class ImpactRequest(BaseModel):
    """Request payload for impact estimation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(
        default_factory=list, description="Scored findings used for impact analysis"
    )
    waves: List[RemediationWave] = Field(default_factory=list, description="Planned remediation waves")
    framework: str = Field("CIS", description="Framework to reuse for compliance coverage estimates")


class RiskCurvePoint(BaseModel):
    """Data point on the risk reduction curve."""

    model_config = ConfigDict(extra="ignore")

    wave: str = Field(..., description="Wave label")
    cumulative_risk_saved: float = Field(..., ge=0, description="Cumulative risk reduction value")
    percent_of_total: float = Field(..., ge=0, le=100, description="Percentage of total risk reduced")


class ImpactEstimateResponse(BaseModel):
    """Response payload for impact estimation."""

    model_config = ConfigDict(extra="ignore")

    readiness_percent: float = Field(0.0, ge=0, le=100, description="Overall readiness percentage")
    compliance_boost: float = Field(0.0, ge=0, le=100, description="Estimated compliance coverage increase")
    residual_risk: float = Field(100.0, ge=0, le=100, description="Residual risk percentage")
    risk_saved_curve: List[RiskCurvePoint] = Field(
        default_factory=list, description="Risk reduction curve data points"
    )
    controls_covered: List[str] = Field(
        default_factory=list, description="Identifiers of controls covered by the plan"
    )


class MappingRequest(BaseModel):
    """Request payload for controls mapping."""

    model_config = ConfigDict(extra="ignore")

    findings: List[CanonicalFinding] = Field(
        default_factory=list, description="Findings to map to controls"
    )
    framework: str = Field("CIS", description="Compliance framework identifier")


class ControlMapping(BaseModel):
    """Row representing a control mapping."""

    model_config = ConfigDict(extra="ignore")

    control: str = Field(..., description="Control identifier")
    title: str = Field(..., description="Control title")
    description: str = Field("", description="Control description")
    finding_id: Optional[str] = Field(None, description="Identifier of the mapped finding")
    cve: Optional[str] = Field(None, description="CVE associated with the finding if present")


class MappingResponse(BaseModel):
    """Response payload for controls mapping."""

    model_config = ConfigDict(extra="ignore")

    framework: str = Field(..., description="Framework identifier")
    coverage: float = Field(0.0, ge=0, le=100, description="Coverage percentage across the framework")
    unique_controls: List[str] = Field(default_factory=list, description="Controls covered by at least one finding")
    mappings: List[ControlMapping] = Field(default_factory=list, description="Detailed mapping rows")
    unmapped: List[str] = Field(default_factory=list, description="Identifiers of findings without any control mapping")


class SummaryRequest(BaseModel):
    """Request payload for summary generation."""

    model_config = ConfigDict(extra="ignore")

    findings: List[ScoreFinding] = Field(default_factory=list, description="Findings included in the summary")
    waves: List[RemediationWave] = Field(default_factory=list, description="Remediation plan included in the summary")
    notes: Optional[str] = Field(None, description="Optional analyst notes")
    impact: Optional[ImpactEstimateResponse] = Field(
        None, description="Pre-computed impact information to embed into the report"
    )
    mapping: Optional[MappingResponse] = Field(
        None, description="Pre-computed control mapping information to embed into the report"
    )


class SummaryGenerateResponse(BaseModel):
    """Response payload for summary generation."""

    model_config = ConfigDict(extra="ignore")

    path: str = Field(..., description="Relative filesystem path where the report was stored")
    html: str = Field(..., description="Rendered HTML contents")


class NLQueryRequest(BaseModel):
    """Request payload for the natural language query endpoint."""

    model_config = ConfigDict(extra="ignore")

    query: str = Field(..., description="Natural language prompt")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Optional context forwarded to the intent resolver"
    )


class NLQueryDetails(BaseModel):
    """Additional metadata returned for natural language queries."""

    model_config = ConfigDict(extra="ignore")

    matched_keywords: List[str] = Field(default_factory=list, description="Keywords detected in the query")
    confidence: float = Field(0.0, ge=0, le=1, description="Confidence in the intent resolution")
    endpoint: Optional[str] = Field(
        None, description="API endpoint that would satisfy the request if applicable"
    )


class NLQueryResponse(BaseModel):
    """Response payload for the natural language query endpoint."""

    model_config = ConfigDict(extra="ignore")

    intent: str = Field(..., description="Resolved intent keyword")
    response: str = Field(..., description="Natural language response returned by the copilot")
    details: NLQueryDetails = Field(default_factory=NLQueryDetails, description="Metadata about the decision")


class FeedbackSubmitRequest(BaseModel):
    """Payload submitted when an analyst provides feedback on a recommendation."""

    model_config = ConfigDict(extra="ignore")

    finding_id: str = Field(..., description="Identifier of the finding receiving feedback")
    action: str = Field(..., description="Type of action recorded e.g. agree/disagree")
    comment: Optional[str] = Field(None, description="Optional analyst note")


class FeedbackResponse(BaseModel):
    """Response confirming that feedback was recorded."""

    model_config = ConfigDict(extra="ignore")

    status: str = Field(..., description="Acknowledgement message")
    path: str = Field(..., description="Path to the feedback log file")
    recorded_at: str = Field(..., description="Timestamp when the feedback was persisted")


class AIProviderOption(BaseModel):
    """Describes an AI provider available to the platform."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Provider identifier")
    label: str = Field(..., description="Human readable label")


class AIProvidersResponse(BaseModel):
    """List of AI providers exposed through the API."""

    model_config = ConfigDict(extra="ignore")

    providers: List[AIProviderOption] = Field(default_factory=list, description="Registered providers")


__all__ = [
    "AssetContext",
    "CanonicalFinding",
    "IngestResponse",
    "ScoringWeights",
    "ScoringConfig",
    "ScoreComponents",
    "ScoreFinding",
    "ScoreTotals",
    "ScoreRequest",
    "ScoreComputeResponse",
    "PlanItem",
    "RemediationWave",
    "PlanTotals",
    "OptimizePlanRequest",
    "OptimizePlanResponse",
    "ImpactRequest",
    "ImpactEstimateResponse",
    "RiskCurvePoint",
    "MappingRequest",
    "MappingResponse",
    "ControlMapping",
    "SummaryRequest",
    "SummaryGenerateResponse",
    "NLQueryRequest",
    "NLQueryResponse",
    "NLQueryDetails",
    "FeedbackSubmitRequest",
    "FeedbackResponse",
    "AIProviderOption",
    "AIProvidersResponse",
]
