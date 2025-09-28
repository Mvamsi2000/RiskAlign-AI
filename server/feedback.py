from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent
FEEDBACK_DIR = BASE_DIR / "output" / "feedback"


def _feedback_file(timestamp: datetime) -> Path:
    return FEEDBACK_DIR / f"feedback-{timestamp.strftime('%Y%m%d')}.jsonl"


def feedback_submit(payload: Dict[str, Any]) -> Dict[str, Any]:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    recorded_at = datetime.now(UTC)
    record = {
        "finding_id": payload.get("finding_id"),
        "action": payload.get("action"),
        "comment": payload.get("comment", ""),
        "recorded_at": recorded_at.isoformat(),
    }
    file_path = _feedback_file(recorded_at)
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")

    return {"status": "recorded", "path": str(file_path), "recorded_at": record["recorded_at"]}


def recent_feedback(limit: int = 10) -> List[Dict[str, Any]]:
    if not FEEDBACK_DIR.exists():
        return []

    entries: List[Dict[str, Any]] = []
    for path in sorted(FEEDBACK_DIR.glob("feedback-*.jsonl"), reverse=True):
        with path.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()
        for line in reversed(lines):
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(entries) >= limit:
                return entries
    return entries
