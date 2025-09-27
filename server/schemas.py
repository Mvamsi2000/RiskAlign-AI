from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AssetContext(BaseModel):
    name: str
    criticality: str = Field(description="Qualitative business criticality label")
    exposure: str = Field(description="Where the asset is exposed (internet/internal/etc)")
    data_sensitivity: Optional[str] = None


class Finding(BaseModel):
    id: str
    title: str
    cve: Optional[str] = None
    cvss: float = Field(ge=0, le=10)
    epss: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    kev: bool = False
    asset: Optional[AssetContext] = None
    effort_hours: Optional[float] = Field(default=None, ge=0.0)
    sla_days: Optional[int] = Field(default=None, ge=0)
    tags: List[str] = Field(default_factory=list)


class Contribution(BaseModel):
    name: str
    weight: float
    value: float
    contribution: float
    description: str


class ScoredFinding(BaseModel):
    id: str
    title: str
    score: float
    priority: str
    contributions: List[Contribution]
    narrative: str
    rules_applied: List[str]


class ScoreSummary(BaseModel):
    counts_by_priority: Dict[str, int]
    generated_at: datetime


class ScoreComputeRequest(BaseModel):
    findings: List[Finding]


class ScoreComputeResponse(BaseModel):
    results: List[ScoredFinding]
    summary: ScoreSummary


class WaveItem(BaseModel):
    id: str
    title: str
    effort_hours: float
    score: float
    risk_reduction: float


class RemediationWave(BaseModel):
    name: str
    total_hours: float
    expected_risk_reduction: float
    items: List[WaveItem]


class OptimizePlanRequest(BaseModel):
    findings: List[Finding]
    max_hours_per_wave: float = Field(default=16, ge=1.0)


class OptimizePlanResponse(BaseModel):
    waves: List[RemediationWave]


class ControlMapping(BaseModel):
    control: str
    description: str
    finding: str


class MapControlsRequest(BaseModel):
    cves: List[str]
    standard: str = "CIS"
    version: Optional[str] = None


class MapControlsResponse(BaseModel):
    mappings: List[ControlMapping]


class ImpactEstimateRequest(BaseModel):
    findings: List[Finding]


class ImpactEstimateResponse(BaseModel):
    breach_reduction: float
    compliance_gain: float
    rationale: str


class NLQueryRequest(BaseModel):
    query: str


class NLQueryResponse(BaseModel):
    intent: str
    response: str
    details: Dict[str, float]


class FeedbackRequest(BaseModel):
    finding_id: str
    action: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    recorded_at: datetime


class SummaryGenerateRequest(BaseModel):
    scope: Optional[str] = Field(default="environment")
    findings: Optional[List[Finding]] = None


class SummaryGenerateResponse(BaseModel):
    html: str
