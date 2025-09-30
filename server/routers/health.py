"""Health and readiness probes for the RiskAlign AI API."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def get_health() -> dict[str, str]:
    """Return a simple liveness heartbeat."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/ready", summary="Readiness probe")
async def get_readiness() -> dict[str, str]:
    """Return readiness information indicating that dependencies are available."""
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
