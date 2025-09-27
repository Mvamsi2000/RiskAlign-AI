from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    ComplianceMappingRequest,
    ComplianceMappingResponse,
    FeedbackRequest,
    FeedbackResponse,
    ImpactEstimateRequest,
    ImpactEstimateResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
    OptimizationPlanRequest,
    OptimizationPlanResponse,
    ScoreComputeRequest,
    ScoreComputeResponse,
    SummaryGenerateRequest,
    SummaryGenerateResponse,
)
from .services.config_loader import load_controls_mapping, load_scoring_config
from .services.feedback import log_feedback
from .services.impact import estimate_impact
from .services.mapping import map_to_controls
from .services.nl_router import handle_nl_query
from .services.optimizer import build_optimization_plan
from .services.scoring import compute_scores
from .services.summary import render_summary
app = FastAPI(
    title="RiskAlign-AI",
    description="Cyber risk decision intelligence MVP exposing scoring, planning, mapping, and narrative endpoints.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/score/compute", response_model=ScoreComputeResponse)
async def score_compute(payload: ScoreComputeRequest) -> ScoreComputeResponse:
    config = load_scoring_config(payload.config_overrides)
    return compute_scores(payload.findings, config)


@app.post("/api/optimize/plan", response_model=OptimizationPlanResponse)
async def optimize_plan(payload: OptimizationPlanRequest) -> OptimizationPlanResponse:
    config = load_scoring_config()
    return build_optimization_plan(payload.findings, config, payload.constraints)


@app.post("/api/map/controls", response_model=ComplianceMappingResponse)
async def map_controls(payload: ComplianceMappingRequest) -> ComplianceMappingResponse:
    mapping = load_controls_mapping(payload.framework)
    if mapping is None:
        raise HTTPException(status_code=404, detail="Requested framework mapping not available")
    return map_to_controls(payload.cves, mapping)


@app.post("/api/impact/estimate", response_model=ImpactEstimateResponse)
async def impact_estimate(payload: ImpactEstimateRequest) -> ImpactEstimateResponse:
    return estimate_impact(payload.findings)


@app.post("/api/summary/generate", response_model=SummaryGenerateResponse)
async def summary_generate(payload: SummaryGenerateRequest) -> SummaryGenerateResponse:
    scoring_config = load_scoring_config()
    return render_summary(payload.scope, payload.findings, scoring_config)


@app.post("/api/nl/query", response_model=NaturalLanguageQueryResponse)
async def nl_query(payload: NaturalLanguageQueryRequest) -> NaturalLanguageQueryResponse:
    scoring_config = load_scoring_config()
    return handle_nl_query(payload.query, payload.findings or [], scoring_config)


@app.post("/api/feedback/submit", response_model=FeedbackResponse)
async def feedback_submit(payload: FeedbackRequest) -> FeedbackResponse:
    log_feedback(payload)
    return FeedbackResponse(status="acknowledged", message="Feedback captured for future weight tuning.")
