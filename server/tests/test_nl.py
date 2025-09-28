from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def test_nl_router_identifies_plan_intent() -> None:
    response = client.post(
        "/api/nl/query",
        json={"query": "Can you plan remediation waves under 10 hours?"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "plan"
    assert payload["details"]["endpoint"] == "/api/optimize/plan"
    assert "plan" in payload["details"]["matched_keywords"]
