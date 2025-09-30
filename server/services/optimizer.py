"""Placeholder optimizer service that returns a single remediation wave."""
from __future__ import annotations

from typing import List

from server.schemas.api import OptimizeRequest, OptimizeResponse, Wave


def generate_plan(payload: OptimizeRequest) -> OptimizeResponse:
    """Return a deterministic remediation plan made of a single wave."""
    if not payload.findings:
        return OptimizeResponse(waves=[], unassigned=[])

    capacity = payload.budget_hours or 40.0
    wave = Wave(
        name="Wave 1",
        order=0,
        capacity_hours=capacity,
        findings=[finding.id for finding in payload.findings],
        total_risk_reduction=sum(getattr(finding, "score", 0.0) for finding in payload.findings),
        estimated_effort_hours=min(capacity, 40.0),
    )

    return OptimizeResponse(waves=[wave], unassigned=[])
