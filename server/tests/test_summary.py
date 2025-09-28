from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def test_summary_generate_creates_file() -> None:
    findings = [
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
    ]

    response = client.post(
        "/api/summary/generate",
        json={"scope": "pilot", "findings": findings, "framework": "CIS"},
    )
    assert response.status_code == 200

    payload = response.json()
    path = Path(payload["path"])
    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
    assert "RiskAlign-AI Summary" in payload["html"]

    path.unlink()
