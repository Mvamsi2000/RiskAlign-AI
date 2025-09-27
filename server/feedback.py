from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Deque, Dict

from .schemas import FeedbackRequest, FeedbackResponse

_HISTORY: Deque[Dict[str, str]] = deque(maxlen=50)


def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    record = {
        "finding_id": request.finding_id,
        "action": request.action,
        "comment": request.comment or "",
        "recorded_at": datetime.utcnow().isoformat(),
    }
    _HISTORY.appendleft(record)

    return FeedbackResponse(status="recorded", recorded_at=datetime.utcnow())


def recent_feedback() -> Deque[Dict[str, str]]:
    return _HISTORY
