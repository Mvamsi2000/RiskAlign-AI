"""Smoke tests for health endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient

from server.app import create_app


client = TestClient(create_app())


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "timestamp" in payload


def test_ready_endpoint_returns_ready() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert "timestamp" in payload
