"""Analyst feedback endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from server.schemas import FeedbackResponse, FeedbackSubmitRequest
from server.services.audit import record_feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("/submit", response_model=FeedbackResponse, summary="Record analyst feedback on a recommendation")
async def submit_feedback(payload: FeedbackSubmitRequest) -> FeedbackResponse:
    return record_feedback(payload)


__all__ = ["router"]
