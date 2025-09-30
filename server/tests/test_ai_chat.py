from __future__ import annotations

import sys

from fastapi.testclient import TestClient
import pytest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from server.ai.provider import AIProviderError
from server.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_ai_chat_handles_provider_error(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    def _raise_error(*args, **kwargs):  # type: ignore[unused-argument]
        raise AIProviderError("provider unavailable")

    monkeypatch.setattr("server.main.chat_with_provider", _raise_error)

    response = client.post(
        "/api/ai/chat",
        json={"messages": [{"role": "user", "content": "hello"}]},
    )
    assert response.status_code == 503
    payload = response.json()
    error_block = payload.get("detail", {}).get("error", {})
    assert error_block.get("code") == "chat_unavailable"
    assert "provider" in (error_block.get("message", "").lower())
