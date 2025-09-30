"""Uvicorn entrypoint for the RiskAlign AI API."""
from __future__ import annotations

import os
from typing import Final

import uvicorn

from .app import create_app

app = create_app()


def run() -> None:
    """Run the Uvicorn development server."""
    host: Final[str] = os.getenv("HOST", "0.0.0.0")
    port: Final[int] = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run("server.main:app", host=host, port=port, reload=reload_flag, factory=False, log_level="info")


if __name__ == "__main__":
    run()
