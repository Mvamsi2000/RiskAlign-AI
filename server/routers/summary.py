"""Summary report endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas.api import SummaryRequest, SummaryResponse
from server.services.report import generate_summary

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.post("/generate", response_model=SummaryResponse, summary="Generate executive summary report")
async def generate(payload: SummaryRequest) -> SummaryResponse:
    """Generate a placeholder executive summary report."""
    return generate_summary(payload)
