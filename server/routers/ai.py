"""AI provider discovery endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.ai.provider import available_providers
from server.schemas import AIProvidersResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/providers", response_model=AIProvidersResponse, summary="List available AI providers")
async def list_providers() -> AIProvidersResponse:
    return AIProvidersResponse(providers=available_providers())


__all__ = ["router"]
