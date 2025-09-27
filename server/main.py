from __future__ import annotations

import json

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import feedback, impact, mapping, nl_router, optimizer, scoring, summary
from .schemas import (
    FeedbackRequest,
    FeedbackResponse,
    ImpactEstimateRequest,
    ImpactEstimateResponse,
    MapControlsRequest,
    MapControlsResponse,
    NLQueryRequest,
    NLQueryResponse,
    OptimizePlanRequest,
    OptimizePlanResponse,
    ScoreComputeRequest,
    ScoreComputeResponse,
    SummaryGenerateRequest,
    SummaryGenerateResponse,
)

app = FastAPI(title="RiskAlign-AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/findings/sample")
def sample_findings() -> List[dict]:
    sample_path = Path(__file__).resolve().parent / "data" / "sample_findings.json"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample data not found")
    return json.loads(sample_path.read_text(encoding="utf-8"))


@app.post("/api/score/compute", response_model=ScoreComputeResponse)
def score_compute(request: ScoreComputeRequest) -> ScoreComputeResponse:
    return scoring.compute_scores(request.findings)


@app.post("/api/optimize/plan", response_model=OptimizePlanResponse)
def optimize_plan(request: OptimizePlanRequest) -> OptimizePlanResponse:
    return optimizer.optimize_plan(request)


@app.post("/api/map/controls", response_model=MapControlsResponse)
def map_controls(request: MapControlsRequest) -> MapControlsResponse:
    return mapping.map_to_controls(request)


@app.post("/api/impact/estimate", response_model=ImpactEstimateResponse)
def impact_estimate(request: ImpactEstimateRequest) -> ImpactEstimateResponse:
    return impact.estimate_impact(request)


@app.post("/api/nl/query", response_model=NLQueryResponse)
def nl_query(request: NLQueryRequest) -> NLQueryResponse:
    return nl_router.route_query(request)


@app.post("/api/summary/generate", response_model=SummaryGenerateResponse)
def summary_generate(request: SummaryGenerateRequest) -> SummaryGenerateResponse:
    return summary.generate_summary(request)


@app.post("/api/feedback/submit", response_model=FeedbackResponse)
def feedback_submit(request: FeedbackRequest) -> FeedbackResponse:
    return feedback.submit_feedback(request)


@app.get("/api/feedback/recent")
def recent_feedback() -> List[dict[str, str]]:
    return list(feedback.recent_feedback())
