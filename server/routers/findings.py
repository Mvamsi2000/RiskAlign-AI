"""Sample findings dataset endpoints."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException

from server.schemas import CanonicalFinding

router = APIRouter(prefix="/api/findings", tags=["findings"])

_SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "samples" / "sample_findings.json"


def _load_sample_findings() -> List[CanonicalFinding]:
    if not _SAMPLE_PATH.exists():
        raise HTTPException(status_code=500, detail="Sample dataset not found")
    with _SAMPLE_PATH.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return [CanonicalFinding.model_validate(item) for item in raw]


@router.get("/sample", response_model=List[CanonicalFinding], summary="Return demo findings dataset")
async def get_sample_findings() -> List[CanonicalFinding]:
    return _load_sample_findings()


__all__ = ["router"]
