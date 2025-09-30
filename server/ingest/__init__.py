"""Ingestion adapters and canonical pipeline."""

from .auto_detect import detect_adapter  # noqa: F401
from .pipeline import IngestStats, run_ingest_pipeline  # noqa: F401

__all__ = ["detect_adapter", "run_ingest_pipeline", "IngestStats"]
