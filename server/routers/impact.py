"""Impact estimation endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas.api import ImpactRequest, ImpactResponse
from server.services.impact import estimate_impact

router = APIRouter(prefix="/api/impact", tags=["impact"])


@router.post("/estimate", response_model=ImpactResponse, summary="Estimate impact and readiness")
async def estimate(payload: ImpactRequest) -> ImpactResponse:
    """Return placeholder impact metrics."""
    return estimate_impact(payload)
