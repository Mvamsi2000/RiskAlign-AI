"""Scoring endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas.api import ScoreRequest, ScoreResponse
from server.services.scoring import score_compute

router = APIRouter(prefix="/api/score", tags=["scoring"])


@router.post("/compute", response_model=ScoreResponse, summary="Compute risk scores for findings")
async def compute_scores(payload: ScoreRequest) -> ScoreResponse:
    """Return placeholder scoring data for the supplied findings."""
    return score_compute(payload)
