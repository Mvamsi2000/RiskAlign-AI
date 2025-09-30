"""End-to-end smoke tests covering the REST surface."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from server.app import create_app

client = TestClient(create_app())

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"


def _fetch_sample_findings():
    response = client.get("/api/findings/sample")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and data
    return data


def test_ingest_pipeline_detects_csv():
    sample_file = SAMPLES_DIR / "Security Vulnerabilities.csv"
    assert sample_file.exists()
    with sample_file.open("rb") as handle:
        files = {"file": (sample_file.name, handle.read(), "text/csv")}
    response = client.post("/api/ingest/upload", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert payload["envelope"]["intent"] == "ingest"
    assert payload["sample"]


def test_scoring_and_plan_flow():
    findings = _fetch_sample_findings()

    score_response = client.post("/api/score/compute", json={"findings": findings})
    assert score_response.status_code == 200
    scored = score_response.json()
    assert scored["totals"]["count"] == len(findings)
    assert scored["findings"][0]["components"]

    plan_response = client.post(
        "/api/optimize/plan",
        json={"findings": scored["findings"], "max_hours_per_wave": 16},
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()
    assert plan["waves"]
    assert plan["totals"]["waves"] >= 1

    impact_response = client.post(
        "/api/impact/estimate",
        json={"findings": scored["findings"], "waves": plan["waves"]},
    )
    assert impact_response.status_code == 200
    impact = impact_response.json()
    assert impact["readiness_percent"] > 0
    assert impact["risk_saved_curve"]

    mapping_response = client.post(
        "/api/map/controls",
        json={"findings": findings, "framework": "CIS"},
    )
    assert mapping_response.status_code == 200
    mapping = mapping_response.json()
    assert mapping["unique_controls"]

    summary_response = client.post(
        "/api/summary/generate",
        json={
            "findings": scored["findings"],
            "waves": plan["waves"],
            "impact": impact,
            "mapping": mapping,
        },
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["path"].startswith("/reports/")
    report_name = summary["path"].split("/reports/")[-1]
    output_dir = Path(__file__).resolve().parents[1] / "output"
    report_path = output_dir / report_name
    assert report_path.exists()
    assert "<html" in summary["html"].lower()

    feedback_response = client.post(
        "/api/feedback/submit",
        json={"finding_id": scored["findings"][0]["id"], "action": "agree"},
    )
    assert feedback_response.status_code == 200
    feedback = feedback_response.json()
    assert Path(feedback["path"]).exists()


def test_nl_query_returns_structured_details():
    response = client.post(
        "/api/nl/query",
        headers={"X-AI-Provider": "local"},
        json={"query": "optimise the remediation plan", "context": {}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] in {"plan", "score", "summary"}
    assert payload["details"]["matched_keywords"]
    assert payload["response"]


def test_ai_providers_endpoint():
    response = client.get("/api/ai/providers")
    assert response.status_code == 200
    data = response.json()
    assert any(provider["id"] == "local" for provider in data["providers"])
