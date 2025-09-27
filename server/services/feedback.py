from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..schemas import FeedbackRequest

LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "feedback.log"


def log_feedback(payload: FeedbackRequest) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "finding_id": payload.finding_id,
        "decision": payload.decision,
        "comment": payload.comment,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
