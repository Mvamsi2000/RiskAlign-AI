from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.main import app


client = TestClient(app)


def test_map_controls_cis() -> None:
    findings = [
        {"id": "F-1", "cve": "CVE-2023-12345", "cvss": 9.0, "epss": 0.3, "mvi": 8.0, "kev": True},
        {"id": "F-2", "cve": "CVE-2024-9876", "cvss": 7.0, "epss": 0.1, "mvi": 5.0, "kev": False},
        {"id": "F-3", "cve": "CVE-2021-0001", "cvss": 5.0, "epss": 0.2, "mvi": 3.0, "kev": False},
    ]

    response = client.post("/api/map/controls", json={"framework": "CIS", "findings": findings})
    assert response.status_code == 200

    payload = response.json()
    assert payload["framework"] == "CIS"
    assert payload["coverage"] == 66.67
    assert sorted(payload["unique_controls"]) == ["CIS 4.1", "CIS 6.2", "CIS 7.6"]
    assert payload["unmapped"] == ["CVE-2021-0001"]

    mapping_entries = {(item["cve"], item["control"]) for item in payload["mappings"]}
    assert ("CVE-2023-12345", "CIS 4.1") in mapping_entries
    assert ("CVE-2024-9876", "CIS 7.6") in mapping_entries
