"""Smoke tests covering the placeholder API contracts."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from server.app import create_app

client = TestClient(create_app())


_CANONICAL_FINDING = {
    "id": "F-001",
    "title": "Sample Finding",
    "description": "Placeholder finding for contract tests.",
}

_SCORE_FINDING = {
    **_CANONICAL_FINDING,
    "score": 5.0,
    "bucket": "medium",
    "effort_hours": 4.0,
}

_WAVE = {
    "name": "Wave 1",
    "order": 0,
    "capacity_hours": 40.0,
    "findings": ["F-001"],
    "total_risk_reduction": 5.0,
    "estimated_effort_hours": 4.0,
}


def test_ingest_upload_returns_preview():
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/api/ingest/upload", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["sample"][0]["id"].startswith("stub::")


def test_scoring_compute_returns_summary():
    response = client.post("/api/score/compute", json={"findings": [_CANONICAL_FINDING]})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["total_findings"] == 1
    assert payload["findings"][0]["bucket"] == "medium"


def test_optimize_plan_returns_wave():
    response = client.post("/api/optimize/plan", json={"findings": [_SCORE_FINDING], "budget_hours": 20})
    assert response.status_code == 200
    payload = response.json()
    assert payload["waves"]
    assert payload["waves"][0]["findings"] == ["F-001"]


def test_impact_estimate_returns_curve():
    response = client.post(
        "/api/impact/estimate",
        json={"findings": [_SCORE_FINDING], "waves": [_WAVE]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["readiness_pct"] > 0
    assert payload["risk_saved_curve"]


def test_mapping_controls_returns_rows():
    response = client.post(
        "/api/map/controls",
        json={"findings": [_CANONICAL_FINDING], "framework": "CIS"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["framework"] == "CIS"


def test_summary_generate_creates_report():
    response = client.post(
        "/api/summary/generate",
        json={"findings": [_SCORE_FINDING], "waves": [_WAVE]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["report_url"].startswith("/reports/")
    report_name = payload["report_url"].split("/reports/")[-1]
    report_path = Path("server/output") / report_name
    assert report_path.exists()


def test_nl_query_returns_intent():
    response = client.post(
        "/api/nl/query",
        headers={"X-AI-Provider": "local"},
        json={"query": "plan quick wins", "context": {}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "plan"
    assert payload["tool_called"] == "plan"
