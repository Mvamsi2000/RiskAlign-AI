"""Ingestion pipeline package exports."""
from __future__ import annotations

from .auto_detect import default_adapters, pick_adapter
from .pipeline import run_ingest_pipeline

__all__ = ["run_ingest_pipeline", "default_adapters", "pick_adapter"]
