"""Natural language query endpoint."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header

from server.ai.chat import handle_chat
from server.schemas.api import NLQueryRequest, NLQueryResponse

router = APIRouter(prefix="/api/nl", tags=["nlq"])


@router.post("/query", response_model=NLQueryResponse, summary="Process a natural-language query")
async def query(
    payload: NLQueryRequest,
    ai_provider: Optional[str] = Header(default=None, alias="X-AI-Provider"),
) -> NLQueryResponse:
    """Return a placeholder NLQ response."""
    chat_result = await handle_chat(payload.query, ai_provider, payload.context)
    return NLQueryResponse(**chat_result)
