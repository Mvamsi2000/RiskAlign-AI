"""Optimization endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas import OptimizePlanRequest, OptimizePlanResponse
from server.services.optimizer import generate_plan

router = APIRouter(prefix="/api/optimize", tags=["optimize"])


@router.post("/plan", response_model=OptimizePlanResponse, summary="Generate remediation plan")
async def create_plan(payload: OptimizePlanRequest) -> OptimizePlanResponse:
    """Generate a greedy remediation plan under the provided constraints."""

    return generate_plan(payload)


__all__ = ["router"]
