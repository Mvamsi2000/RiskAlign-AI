from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def test_optimize_plan_greedy_split() -> None:
    payload = {
        "max_hours_per_wave": 8,
        "findings": [
            {
                "id": "F-1",
                "title": "Critical perimeter flaw",
                "cvss": 9.0,
                "epss": 0.3,
                "mvi": 8.0,
                "kev": True,
                "effort_hours": 6.0,
                "asset": {
                    "name": "edge-proxy",
                    "criticality": "critical",
                    "exposure": "internet",
                    "data_sensitivity": "pci",
                },
            },
            {
                "id": "F-2",
                "title": "Internal service patch",
                "cvss": 7.0,
                "epss": 0.1,
                "mvi": 5.0,
                "kev": False,
                "effort_hours": 5.0,
                "asset": {
                    "name": "billing-api",
                    "criticality": "high",
                    "exposure": "internal",
                    "data_sensitivity": "pii",
                },
            },
            {
                "id": "F-3",
                "title": "Middleware update",
                "cvss": 5.0,
                "epss": 0.5,
                "mvi": 3.0,
                "kev": False,
                "effort_hours": 4.0,
                "asset": {
                    "name": "data-pipeline",
                    "criticality": "medium",
                    "exposure": "internal",
                },
            },
        ],
    }

    response = client.post("/api/optimize/plan", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["totals"]["waves"] == 3
    assert body["totals"]["total_hours"] == 15.0
    assert body["totals"]["total_risk_saved"] == 18.55

    wave_names = [wave["name"] for wave in body["waves"]]
    assert wave_names == ["Wave 1", "Wave 2", "Wave 3"]

    first_wave = body["waves"][0]
    assert first_wave["total_hours"] == 6.0
    assert first_wave["risk_saved"] == 9.0
    assert first_wave["items"][0]["id"] == "F-1"
    assert first_wave["items"][0]["priority"] == "High"

    second_wave = body["waves"][1]
    assert second_wave["items"][0]["id"] == "F-3"
    assert second_wave["risk_saved"] == 4.55

    third_wave = body["waves"][2]
    assert third_wave["items"][0]["id"] == "F-2"
    assert third_wave["risk_saved"] == 5.0
