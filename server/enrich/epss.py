from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=1)
def _load_epss() -> Dict[str, float]:
    path = _DATA_DIR / "epss.csv"
    if not path.exists():
        return {}

    scores: Dict[str, float] = {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                cve = (row.get("cve") or row.get("CVE") or "").strip().upper()
                value = row.get("epss") or row.get("EPSS")
                if not cve or value is None:
                    continue
                try:
                    scores[cve] = float(value)
                except ValueError:
                    continue
    except OSError:
        return {}
    return scores


def lookup_epss(cve: str | None) -> Optional[float]:
    """Return the EPSS score for the given CVE if cached locally."""

    if not cve:
        return None
    return _load_epss().get(cve.upper())


__all__ = ["lookup_epss"]
