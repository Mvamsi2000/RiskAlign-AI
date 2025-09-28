from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def test_score_compute_smoke() -> None:
    payload = {
        "findings": [
            {
                "id": "F-1",
                "title": "Example CVE",
                "cvss": 8.0,
                "epss": 0.2,
                "mvi": 6.0,
                "kev": True,
                "effort_hours": 4.0,
                "asset": {
                    "name": "api-gateway",
                    "criticality": "high",
                    "exposure": "internet",
                    "data_sensitivity": "pii",
                },
            }
        ]
    }

    response = client.post("/api/score/compute", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["totals"]["count"] == 1
    assert body["totals"]["by_priority"]["High"] == 1

    finding = body["findings"][0]
    assert finding["id"] == "F-1"
    assert finding["priority"] == "High"
    assert finding["effort_hours"] == 4.0
    assert finding["context_multiplier"] == 1.39
    assert finding["components"]["cvss"] == 4.8
    assert finding["components"]["epss"] == 0.5
    assert finding["components"]["mvi"] == 0.6
    assert finding["components"]["kev"] == 1.0
    assert finding["components"]["context"] == 0.14
    assert finding["score"] == 7.04
