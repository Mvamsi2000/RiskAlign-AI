"""Simple audit logging utilities."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from server.schemas import FeedbackResponse, FeedbackSubmitRequest

_LOG_DIR = Path(__file__).resolve().parent.parent / "output"
_LOG_FILE = _LOG_DIR / "feedback.log.jsonl"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_feedback(payload: FeedbackSubmitRequest) -> FeedbackResponse:
    """Append analyst feedback to a JSONL file for later analysis."""

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    event: Dict[str, Any] = {
        "finding_id": payload.finding_id,
        "action": payload.action,
        "comment": payload.comment,
        "recorded_at": _timestamp(),
    }
    with _LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    return FeedbackResponse(status="recorded", path=str(_LOG_FILE), recorded_at=event["recorded_at"])


__all__ = ["record_feedback"]
