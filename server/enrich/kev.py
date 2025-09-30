from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Set

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=1)
def _load_kev() -> Set[str]:
    path = _DATA_DIR / "kev.txt"
    if not path.exists():
        return set()

    try:
        values = {
            line.strip().upper()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
    except OSError:
        return set()
    return values


def is_kev(cve: str | None) -> bool:
    """Return True when the CVE is present in the local KEV cache."""

    if not cve:
        return False
    return cve.upper() in _load_kev()


__all__ = ["is_kev"]
