"""Impact estimation endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas import ImpactEstimateResponse, ImpactRequest
from server.services.impact import estimate_impact

router = APIRouter(prefix="/api/impact", tags=["impact"])


@router.post("/estimate", response_model=ImpactEstimateResponse, summary="Estimate impact and readiness")
async def estimate(payload: ImpactRequest) -> ImpactEstimateResponse:
    """Return readiness, residual risk and compliance boost metrics."""

    return estimate_impact(payload)


__all__ = ["router"]
