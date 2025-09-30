"""Control mapping endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas import MappingRequest, MappingResponse
from server.services.mapping import map_to_controls

router = APIRouter(prefix="/api/map", tags=["mapping"])


@router.post("/controls", response_model=MappingResponse, summary="Map findings to compliance controls")
async def map_controls(payload: MappingRequest) -> MappingResponse:
    """Return compliance control coverage for the provided findings."""

    return map_to_controls(payload)


__all__ = ["router"]
