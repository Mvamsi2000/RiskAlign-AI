"""Ingestion endpoints for uploading security artifacts."""
from __future__ import annotations

from typing import Final

from fastapi import APIRouter, File, HTTPException, UploadFile

from server.ingest import run_ingest_pipeline
from server.schemas import IngestResponse

router = APIRouter(prefix="/api/ingest", tags=["ingest"])

_PREVIEW_LIMIT: Final[int] = 5


@router.post("/upload", response_model=IngestResponse, summary="Upload an artifact for ingestion")
async def upload_artifact(file: UploadFile = File(...)) -> IngestResponse:
    """Accept an artifact upload, detect its structure and return a preview."""

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file was empty")

    findings, envelope = run_ingest_pipeline(file.filename or "artifact", data)
    sample = findings[:_PREVIEW_LIMIT]

    return IngestResponse(
        count=len(findings),
        sample=sample,
        envelope=envelope.model_dump(mode="json"),
    )


__all__ = ["router"]
