from __future__ import annotations

from pathlib import Path
from typing import Iterator
import sys

from fastapi.testclient import TestClient
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.ingest.pipeline import run_ingest_pipeline
from server.main import app

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def cleanup_namespace() -> Iterator[str]:
    namespace = "test-ingest"
    output_dir = Path(__file__).resolve().parents[1] / "output" / namespace / "canonical"
    yield namespace
    if output_dir.exists():
        for path in output_dir.glob("*.jsonl"):
            path.unlink()


def test_auto_detect_nessus_ingest(cleanup_namespace: str) -> None:
    sample_path = DATA_DIR / "sample_scan.nessus"
    content = sample_path.read_bytes()

    stats = run_ingest_pipeline(content, sample_path.name, cleanup_namespace)

    assert stats.detected == "nessus_xml"
    assert stats.accepted > 0
    assert stats.path.exists()


def test_canonical_endpoint_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app)

    response = client.get("/api/findings/canonical", headers={"X-Namespace": "empty-test"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["fallback"] is True
    assert payload["count"] > 0
