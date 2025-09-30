"""Scoring endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas import ScoreComputeResponse, ScoreRequest
from server.services.scoring import score_compute

router = APIRouter(prefix="/api/score", tags=["scoring"])


@router.post("/compute", response_model=ScoreComputeResponse, summary="Compute risk scores for findings")
async def compute_scores(payload: ScoreRequest) -> ScoreComputeResponse:
    """Return detailed scoring data for the supplied findings."""

    return score_compute(payload)


__all__ = ["router"]
