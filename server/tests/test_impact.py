from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def _sample_findings() -> list[dict[str, object]]:
    return [
        {
            "id": "F-1",
            "title": "Critical perimeter flaw",
            "cve": "CVE-2023-12345",
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
            "cve": "CVE-2024-9876",
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
            "cve": "CVE-2022-56789",
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
    ]


def test_impact_estimate_returns_curve_and_boost() -> None:
    findings = _sample_findings()
    plan_response = client.post(
        "/api/optimize/plan",
        json={"max_hours_per_wave": 8, "findings": findings},
    )
    assert plan_response.status_code == 200

    plan = plan_response.json()
    waves = plan["waves"]
    impact_response = client.post(
        "/api/impact/estimate",
        json={"findings": findings, "waves": waves},
    )
    assert impact_response.status_code == 200

    payload = impact_response.json()
    assert 0 <= payload["readiness_percent"] <= 100
    assert payload["risk_saved_curve"]
    assert len(payload["risk_saved_curve"]) == len(waves)
    assert payload["risk_saved_curve"][-1]["percent_of_total"] == 100.0

    controls = payload["controls_covered"]
    assert "CIS 4.1" in controls
    assert "CIS 7.6" in controls
    assert payload["compliance_boost"] > 0
    assert payload["compliance_boost"] <= 100
