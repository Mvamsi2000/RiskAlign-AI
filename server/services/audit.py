"""Placeholder audit service."""
from __future__ import annotations

from datetime import datetime
from typing import List

from server.schemas import CanonicalFinding


def record_findings(findings: List[CanonicalFinding]) -> dict[str, str]:
    """Return a stubbed audit receipt."""
    return {"status": "logged", "timestamp": datetime.utcnow().isoformat()}
