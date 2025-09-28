from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .feedback import feedback_submit, recent_feedback
from .impact import impact_estimate
from .nl_router import nl_query
from .mapping import map_to_controls
from .optimizer import optimize_plan
from .scoring import score_compute
from .summary import generate_summary


class AssetContext(BaseModel):
    name: Optional[str] = None
    criticality: Optional[str] = Field(default=None, description="Business criticality label")
    exposure: Optional[str] = Field(default=None, description="Exposure surface (internet/internal/isolated)")
    data_sensitivity: Optional[str] = Field(default=None, description="Data classification for the asset")


class FindingInput(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    cve: Optional[str] = None
    cvss: float = Field(ge=0.0, le=10.0)
    epss: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    mvi: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    kev: bool = False
    asset: Optional[AssetContext] = None
    effort_hours: Optional[float] = Field(default=0.0, ge=0.0)


class ScoreComponents(BaseModel):
    cvss: float
    epss: float
    mvi: float
    kev: float
    context: float


class ScoreFinding(BaseModel):
    id: Optional[str]
    title: Optional[str]
    score: float
    priority: str
    effort_hours: float
    components: ScoreComponents
    context_multiplier: float


class ScoreTotals(BaseModel):
    count: int
    total_score: float
    average_score: float
    total_effort_hours: float
    by_priority: Dict[str, int]


class ScoreComputeRequest(BaseModel):
    findings: List[FindingInput]
    config: Optional[Dict[str, Any]] = Field(default=None, description="Optional overrides for scoring weights")


class ScoreComputeResponse(BaseModel):
    findings: List[ScoreFinding]
    totals: ScoreTotals


class WaveItem(BaseModel):
    id: Optional[str]
    title: Optional[str]
    effort_hours: float
    score: float
    risk_saved: float
    priority: str


class RemediationWave(BaseModel):
    name: str
    total_hours: float
    risk_saved: float
    items: List[WaveItem]


class PlanTotals(BaseModel):
    waves: int
    total_hours: float
    total_risk_saved: float


class OptimizePlanRequest(BaseModel):
    findings: List[FindingInput]
    max_hours_per_wave: float = Field(default=16.0, gt=0.0)
    config: Optional[Dict[str, Any]] = Field(default=None, description="Optional overrides for scoring weights")


class OptimizePlanResponse(BaseModel):
    waves: List[RemediationWave]
    totals: PlanTotals


class RiskSavedPoint(BaseModel):
    wave: str
    cumulative_risk_saved: float
    percent_of_total: float


class ImpactEstimateRequest(BaseModel):
    findings: List[FindingInput]
    waves: List[RemediationWave]


class ImpactEstimateResponse(BaseModel):
    readiness_percent: float
    risk_saved_curve: List[RiskSavedPoint]
    compliance_boost: float
    controls_covered: List[str]


class ControlMapping(BaseModel):
    cve: str
    control: str
    description: str
    finding_id: Optional[str] = None


class MapControlsRequest(BaseModel):
    findings: List[FindingInput]
    framework: str = Field(default="CIS")


class MapControlsResponse(BaseModel):
    framework: str
    coverage: float
    unique_controls: List[str]
    mappings: List[ControlMapping]
    unmapped: List[str]


class SummaryGenerateRequest(BaseModel):
    findings: Optional[List[FindingInput]] = None
    scope: Optional[str] = Field(default="environment")
    framework: str = Field(default="CIS")
    max_hours_per_wave: float = Field(default=16.0, gt=0.0)


class SummaryGenerateResponse(BaseModel):
    path: str
    html: str


class NLQueryRequest(BaseModel):
    query: str


class NLQueryResponse(BaseModel):
    intent: str
    response: str
    details: Dict[str, Any]


class FeedbackRequest(BaseModel):
    finding_id: str
    action: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    path: str
    recorded_at: str


app = FastAPI(title="RiskAlign-AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/findings/sample")
def sample_findings() -> List[Dict[str, Any]]:
    sample_path = Path(__file__).resolve().parent / "data" / "sample_findings.json"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample data not found")
    return json.loads(sample_path.read_text(encoding="utf-8"))


@app.post("/api/score/compute", response_model=ScoreComputeResponse)
def compute_scores(request: ScoreComputeRequest) -> ScoreComputeResponse:
    payload = score_compute([finding.model_dump() for finding in request.findings], cfg=request.config)
    return ScoreComputeResponse.model_validate(payload)


@app.post("/api/optimize/plan", response_model=OptimizePlanResponse)
def plan_remediation(request: OptimizePlanRequest) -> OptimizePlanResponse:
    findings_payload = [finding.model_dump() for finding in request.findings]
    scored_payload = score_compute(findings_payload, cfg=request.config)
    plan_payload = optimize_plan(
        findings_payload,
        max_hours_per_wave=request.max_hours_per_wave,
        scored=scored_payload["findings"],
        config=request.config,
    )
    return OptimizePlanResponse.model_validate(plan_payload)


@app.post("/api/impact/estimate", response_model=ImpactEstimateResponse)
def estimate_impact(request: ImpactEstimateRequest) -> ImpactEstimateResponse:
    findings_payload = [finding.model_dump() for finding in request.findings]
    waves_payload = [wave.model_dump() for wave in request.waves]
    payload = impact_estimate(waves_payload, findings_payload)
    return ImpactEstimateResponse.model_validate(payload)


@app.post("/api/map/controls", response_model=MapControlsResponse)
def map_controls_endpoint(request: MapControlsRequest) -> MapControlsResponse:
    findings_payload = [finding.model_dump() for finding in request.findings]
    payload = map_to_controls(findings_payload, framework=request.framework)
    return MapControlsResponse.model_validate(payload)


@app.post("/api/summary/generate", response_model=SummaryGenerateResponse)
def generate_summary_endpoint(request: SummaryGenerateRequest) -> SummaryGenerateResponse:
    findings_payload = None
    if request.findings is not None:
        findings_payload = [finding.model_dump() for finding in request.findings]
    payload = generate_summary(
        findings=findings_payload,
        scope=request.scope or "environment",
        framework=request.framework,
        max_hours_per_wave=request.max_hours_per_wave,
    )
    return SummaryGenerateResponse.model_validate(payload)


@app.post("/api/nl/query", response_model=NLQueryResponse)
def nl_query_endpoint(request: NLQueryRequest) -> NLQueryResponse:
    payload = nl_query(request.model_dump())
    return NLQueryResponse.model_validate(payload)


@app.post("/api/feedback/submit", response_model=FeedbackResponse)
def feedback_submit_endpoint(request: FeedbackRequest) -> FeedbackResponse:
    payload = feedback_submit(request.model_dump())
    return FeedbackResponse.model_validate(payload)


@app.get("/api/feedback/recent")
def recent_feedback_endpoint(limit: int = 10) -> List[Dict[str, Any]]:
    return recent_feedback(limit)
