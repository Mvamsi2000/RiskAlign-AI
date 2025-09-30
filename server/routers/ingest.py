"""Ingestion endpoints for uploading security artifacts."""
from __future__ import annotations

from typing import Final

from fastapi import APIRouter, File, UploadFile

from server.schemas import CanonicalFinding
from server.schemas.api import IngestResponse

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

_PREVIEW_LIMIT: Final[int] = 4096


@router.post("/upload", response_model=IngestResponse, summary="Upload an artifact for ingestion")
async def upload_artifact(file: UploadFile = File(...)) -> IngestResponse:
    """Accept an artifact upload and return a lightweight preview."""
    head = await file.read(_PREVIEW_LIMIT)
    await file.seek(0)

    if not head:
        return IngestResponse(count=0, sample=[])

    preview = CanonicalFinding(
        id=f"stub::{file.filename}",
        title=f"Preview of {file.filename}",
        description="Ingestion pipeline not yet implemented; this is a placeholder preview.",
        tags=["preview", "stub"],
    )

    return IngestResponse(count=1, sample=[preview])
