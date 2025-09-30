from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .ai.chat import chat_with_provider
from .ai.provider import AIProviderError
from .ai.resolve import ProviderResolutionError
from .core.tenancy import get_namespace, namespace_ai_config_path
from .feedback import feedback_submit, recent_feedback
from .impact import impact_estimate
from .ingest.pipeline import (
    IngestError,
    list_canonical_batches,
    load_canonical_batch,
    run_ingest_pipeline,
)
from .mapping import map_to_controls
from .nl_router import nl_query
from .optimizer import optimize_plan
from .scoring import score_compute
from .schemas import export_json_schemas
from .summary import generate_summary

logger = logging.getLogger(__name__)

app = FastAPI(title="RiskAlign-AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

export_json_schemas()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
_SAMPLE_FINDINGS_PATH = Path(__file__).resolve().parent / "data" / "sample_findings.json"


def _require_admin(request: Request) -> None:
    if not ADMIN_API_KEY:
        return
    header = request.headers.get("X-Admin-Key")
    if header != ADMIN_API_KEY:
        _raise_http_error(
            status.HTTP_401_UNAUTHORIZED,
            code="unauthorised",
            message="Invalid admin key for configuration change",
        )


def _raise_http_error(status_code: int, *, code: str, message: str, details: Optional[Mapping[str, Any]] = None) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={"error": {"code": code, "message": message, "details": details or {}}},
    )


def _load_ai_config(namespace: str) -> Dict[str, Any]:
    config_path = namespace_ai_config_path(namespace)
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_sample_findings() -> List[Dict[str, Any]]:
    if not _SAMPLE_FINDINGS_PATH.exists():
        return []
    try:
        return json.loads(_SAMPLE_FINDINGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _default_findings(namespace: str, batch: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str], bool]:
    canonical, selected = load_canonical_batch(namespace, batch)
    if canonical:
        return canonical, selected, False
    return _load_sample_findings(), None, True


def _count_findings(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())
    except OSError:
        return 0


def _infer_created_at(path: Path) -> datetime:
    try:
        return datetime.strptime(path.stem, "%Y%m%d-%H%M%S")
    except ValueError:
        return datetime.fromtimestamp(path.stat().st_mtime)


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
    findings: Optional[List[FindingInput]] = None
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
    findings: Optional[List[FindingInput]] = None
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
    findings: Optional[List[FindingInput]] = None
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
    findings: Optional[List[FindingInput]] = None
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


class AIProviderInfo(BaseModel):
    id: str
    label: str


class AIProvidersResponse(BaseModel):
    providers: List[AIProviderInfo]


class AIConfigRequest(BaseModel):
    ai_provider: str = Field(pattern="^(local|online)$")


class AIConfigResponse(BaseModel):
    namespace: str
    ai_provider: str


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


class IngestUploadResponse(BaseModel):
    detected: str
    adapter_label: str
    count: int
    accepted: int
    rejected: int
    path: str
    sample: List[Dict[str, Any]]


class CanonicalBatchInfo(BaseModel):
    name: str
    path: str
    findings: int
    created_at: datetime


class CanonicalBatchesResponse(BaseModel):
    namespace: str
    batches: List[CanonicalBatchInfo]


class CanonicalFindingsResponse(BaseModel):
    namespace: str
    batch: Optional[str]
    fallback: bool
    findings: List[Dict[str, Any]]
    count: int


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    provider: str
    messages: List[ChatMessage]


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/findings/sample")
def sample_findings() -> List[Dict[str, Any]]:
    data = _load_sample_findings()
    if not data:
        _raise_http_error(status.HTTP_404_NOT_FOUND, code="not_found", message="Sample data not found")
    return data


@app.get("/api/ingest/batches", response_model=CanonicalBatchesResponse)
def list_batches(request: Request) -> CanonicalBatchesResponse:
    namespace = get_namespace(request)
    batches = [
        CanonicalBatchInfo(
            name=name,
            path=str(path),
            findings=_count_findings(path),
            created_at=_infer_created_at(path),
        )
        for name, path in list_canonical_batches(namespace)
    ]
    return CanonicalBatchesResponse(namespace=namespace, batches=batches)


@app.get("/api/findings/canonical", response_model=CanonicalFindingsResponse)
def canonical_findings(request: Request, batch: Optional[str] = None) -> CanonicalFindingsResponse:
    namespace = get_namespace(request)
    findings, selected, fallback = _default_findings(namespace, batch)
    return CanonicalFindingsResponse(
        namespace=namespace,
        batch=selected,
        fallback=fallback,
        findings=findings,
        count=len(findings),
    )


@app.post("/api/ingest/upload", response_model=IngestUploadResponse)
async def ingest_upload(request: Request, file: UploadFile = File(...)) -> IngestUploadResponse:
    namespace = get_namespace(request)
    content = await file.read()
    try:
        stats = run_ingest_pipeline(content, file.filename or "upload", namespace)
    except IngestError as exc:
        _raise_http_error(status.HTTP_400_BAD_REQUEST, code="ingest_error", message=str(exc))
    return IngestUploadResponse(
        detected=stats.detected,
        adapter_label=stats.adapter_label,
        count=stats.count,
        accepted=stats.accepted,
        rejected=stats.rejected,
        path=str(stats.path),
        sample=stats.sample,
    )


@app.post("/api/score/compute", response_model=ScoreComputeResponse)
def compute_scores(payload: ScoreComputeRequest, request: Request) -> ScoreComputeResponse:
    namespace = get_namespace(request)
    findings_payload = [finding.model_dump() for finding in payload.findings] if payload.findings else None
    if not findings_payload:
        findings_payload, _, _ = _default_findings(namespace)
    result = score_compute(findings_payload, cfg=payload.config)
    return ScoreComputeResponse.model_validate(result)


@app.post("/api/optimize/plan", response_model=OptimizePlanResponse)
def plan_remediation(payload: OptimizePlanRequest, request: Request) -> OptimizePlanResponse:
    namespace = get_namespace(request)
    findings_payload = [finding.model_dump() for finding in payload.findings] if payload.findings else None
    if not findings_payload:
        findings_payload, _, _ = _default_findings(namespace)
    scored_payload = score_compute(findings_payload, cfg=payload.config)
    plan_payload = optimize_plan(
        findings_payload,
        max_hours_per_wave=payload.max_hours_per_wave,
        scored=scored_payload["findings"],
        config=payload.config,
    )
    return OptimizePlanResponse.model_validate(plan_payload)


@app.post("/api/impact/estimate", response_model=ImpactEstimateResponse)
def estimate_impact(payload: ImpactEstimateRequest, request: Request) -> ImpactEstimateResponse:
    namespace = get_namespace(request)
    findings_payload = [finding.model_dump() for finding in payload.findings] if payload.findings else None
    if not findings_payload:
        findings_payload, _, _ = _default_findings(namespace)
    waves_payload = [wave.model_dump() for wave in payload.waves]
    result = impact_estimate(waves_payload, findings_payload)
    return ImpactEstimateResponse.model_validate(result)


@app.post("/api/map/controls", response_model=MapControlsResponse)
def map_controls_endpoint(payload: MapControlsRequest, request: Request) -> MapControlsResponse:
    namespace = get_namespace(request)
    findings_payload = [finding.model_dump() for finding in payload.findings] if payload.findings else None
    if not findings_payload:
        findings_payload, _, _ = _default_findings(namespace)
    result = map_to_controls(findings_payload, framework=payload.framework)
    return MapControlsResponse.model_validate(result)


@app.post("/api/summary/generate", response_model=SummaryGenerateResponse)
def generate_summary_endpoint(payload: SummaryGenerateRequest, request: Request) -> SummaryGenerateResponse:
    namespace = get_namespace(request)
    findings_payload = [finding.model_dump() for finding in payload.findings] if payload.findings else None
    tenant_config = _load_ai_config(namespace)
    summary_payload = generate_summary(
        findings=findings_payload,
        scope=payload.scope or "environment",
        framework=payload.framework,
        max_hours_per_wave=payload.max_hours_per_wave,
        request=request,
        tenant_config=tenant_config,
        namespace=namespace,
    )
    return SummaryGenerateResponse.model_validate(summary_payload)


@app.post("/api/ai/chat", response_model=ChatResponse)
def ai_chat_endpoint(payload: ChatRequest, request: Request) -> ChatResponse:
    namespace = get_namespace(request)
    tenant_config = _load_ai_config(namespace)
    try:
        result = chat_with_provider(
            request,
            [message.model_dump() for message in payload.messages],
            tenant_config=tenant_config,
            namespace=namespace,
        )
    except (ProviderResolutionError, ValueError) as exc:
        _raise_http_error(status.HTTP_400_BAD_REQUEST, code="chat_error", message=str(exc))
    except AIProviderError as exc:
        _raise_http_error(status.HTTP_503_SERVICE_UNAVAILABLE, code="chat_unavailable", message=str(exc))

    return ChatResponse.model_validate(result)


@app.post("/api/nl/query", response_model=NLQueryResponse)
def nl_query_endpoint(payload: NLQueryRequest) -> NLQueryResponse:
    result = nl_query(payload.model_dump())
    return NLQueryResponse.model_validate(result)


@app.post("/api/feedback/submit", response_model=FeedbackResponse)
def feedback_submit_endpoint(payload: FeedbackRequest) -> FeedbackResponse:
    result = feedback_submit(payload.model_dump())
    return FeedbackResponse.model_validate(result)


@app.get("/api/feedback/recent")
def recent_feedback_endpoint(limit: int = 10) -> List[Dict[str, Any]]:
    return recent_feedback(limit)


@app.get("/api/ai/providers", response_model=AIProvidersResponse)
def list_ai_providers() -> AIProvidersResponse:
    providers = [
        AIProviderInfo(id="local", label="Local (Ollama)"),
        AIProviderInfo(id="online", label="Online (OpenAI)"),
    ]
    return AIProvidersResponse(providers=providers)


@app.post("/api/ai/config", response_model=AIConfigResponse)
def update_ai_config(request: Request, payload: AIConfigRequest) -> AIConfigResponse:
    _require_admin(request)
    namespace = get_namespace(request)
    config_path = namespace_ai_config_path(namespace)
    config_path.write_text(
        json.dumps({"ai_provider": payload.ai_provider}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return AIConfigResponse(namespace=namespace, ai_provider=payload.ai_provider)
