from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ExposureLevel(str, Enum):
    EXTERNAL = "external"
    INTERNAL = "internal"
    PARTIAL = "partial"


class DataSensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    HIGH = "high"


class EffortBucket(str, Enum):
    QUICK_WIN = "quick_win"
    MODERATE = "moderate"
    INTENSIVE = "intensive"


class Finding(BaseModel):
    id: str
    title: str
    cve: Optional[str] = None
    description: str
    cvss: float = Field(..., ge=0, le=10)
    epss: float = Field(..., ge=0, le=1)
    kev: bool = False
    asset_criticality: int = Field(..., ge=1, le=5)
    exposure: ExposureLevel = ExposureLevel.INTERNAL
    effort_hours: float = Field(..., ge=0)
    data_sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    effort_bucket: EffortBucket = EffortBucket.MODERATE
    business_owner: Optional[str] = None


class ScoreContribution(BaseModel):
    signal: str
    weight: float
    value: float
    impact: float
    rationale: str


class ScoredFinding(BaseModel):
    finding: Finding
    score: float
    priority: str
    contributions: List[ScoreContribution]
    recommended_action: str


class ScoreComputeRequest(BaseModel):
    findings: List[Finding]
    config_overrides: Optional[Dict[str, float]] = None


class ScoreComputeResponse(BaseModel):
    findings: List[ScoredFinding]


class OptimizationConstraint(BaseModel):
    max_hours: Optional[float] = None
    waves: int = 3


class RemediationItem(BaseModel):
    finding_id: str
    title: str
    wave: int
    estimated_hours: float
    score: float
    expected_risk_reduction: float


class OptimizationPlanRequest(BaseModel):
    findings: List[Finding]
    constraints: Optional[OptimizationConstraint] = None


class OptimizationPlanResponse(BaseModel):
    plan: List[RemediationItem]
    summary: str


class ComplianceMappingRequest(BaseModel):
    cves: List[str]
    framework: str = "cis"


class ControlMapping(BaseModel):
    control: str
    title: str
    description: str


class ComplianceMappingResponse(BaseModel):
    mappings: Dict[str, List[ControlMapping]]


class ImpactEstimateRequest(BaseModel):
    findings: List[Finding]


class ImpactEstimate(BaseModel):
    breach_cost: float
    compliance_gain: float
    risk_reduction: float


class ImpactEstimateResponse(BaseModel):
    impact: ImpactEstimate


class SummaryGenerateRequest(BaseModel):
    scope: str
    findings: List[Finding]


class SummaryGenerateResponse(BaseModel):
    html: str


class NaturalLanguageQueryRequest(BaseModel):
    query: str
    findings: Optional[List[Finding]] = None


class NaturalLanguageQueryResponse(BaseModel):
    intent: str
    result: Dict[str, str]


class FeedbackRequest(BaseModel):
    finding_id: str
    decision: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str
