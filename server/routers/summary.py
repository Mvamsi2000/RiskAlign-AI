"""Summary generation endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas import (
    ImpactRequest,
    MappingRequest,
    SummaryGenerateResponse,
    SummaryRequest,
)
from server.services.impact import estimate_impact
from server.services.mapping import map_to_controls
from server.services.report import generate_summary

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.post("/generate", response_model=SummaryGenerateResponse, summary="Render executive summary")
async def generate(payload: SummaryRequest) -> SummaryGenerateResponse:
    """Render the executive HTML summary and persist it to disk."""

    impact = payload.impact or estimate_impact(
        ImpactRequest(findings=payload.findings, waves=payload.waves, framework="CIS")
    )
    mapping = payload.mapping or map_to_controls(
        MappingRequest(findings=payload.findings, framework="CIS")
    )
    enriched = SummaryRequest(
        findings=payload.findings,
        waves=payload.waves,
        notes=payload.notes,
        impact=impact,
        mapping=mapping,
    )
    return generate_summary(enriched)


__all__ = ["router"]
