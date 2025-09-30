"""Application factory for the RiskAlign AI API."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ALLOWED_ORIGINS: Iterable[str] = ("http://127.0.0.1:5173", "http://localhost:5173")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="RiskAlign AI API",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/reports", StaticFiles(directory=output_dir), name="reports")

    from .routers import ai, feedback, findings, health, impact, ingest, mapping, nlq, optimize, scoring, summary

    app.include_router(health.router)
    app.include_router(findings.router)
    app.include_router(ai.router)
    app.include_router(ingest.router)
    app.include_router(scoring.router)
    app.include_router(optimize.router)
    app.include_router(impact.router)
    app.include_router(mapping.router)
    app.include_router(summary.router)
    app.include_router(nlq.router)
    app.include_router(feedback.router)

    return app


__all__ = ["create_app"]
