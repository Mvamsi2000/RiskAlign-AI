from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def test_feedback_submission_appends_jsonl(tmp_path: Path) -> None:
    feedback_dir = Path("server/output/feedback")
    if feedback_dir.exists():
        for existing in feedback_dir.glob("feedback-*.jsonl"):
            existing.unlink()

    response = client.post(
        "/api/feedback/submit",
        json={"finding_id": "F-1", "action": "agree", "comment": "Great priority"},
    )
    assert response.status_code == 200
    payload = response.json()
    file_path = Path(payload["path"])
    assert file_path.exists()

    lines = file_path.read_text(encoding="utf-8").strip().splitlines()
    assert lines
    record = json.loads(lines[-1])
    assert record["finding_id"] == "F-1"
    assert record["action"] == "agree"

    file_path.unlink()
