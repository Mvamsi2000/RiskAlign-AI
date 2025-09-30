"""Controls mapping endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas.api import MappingRequest, MappingResponse
from server.services.mapping import map_to_controls

router = APIRouter(prefix="/api/map", tags=["mapping"])


@router.post("/controls", response_model=MappingResponse, summary="Map findings to controls")
async def map_controls(payload: MappingRequest) -> MappingResponse:
    """Return placeholder control mapping information."""
    return map_to_controls(payload)
