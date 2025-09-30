"""Optimization endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas.api import OptimizeRequest, OptimizeResponse
from server.services.optimizer import generate_plan

router = APIRouter(prefix="/api/optimize", tags=["optimize"])


@router.post("/plan", response_model=OptimizeResponse, summary="Generate remediation plan")
async def create_plan(payload: OptimizeRequest) -> OptimizeResponse:
    """Return a placeholder remediation plan."""
    return generate_plan(payload)
