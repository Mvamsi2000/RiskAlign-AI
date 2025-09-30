from __future__ import annotations

import csv
import io
from typing import Iterable, Iterator, Mapping

from .base import AdapterBase
from ..schemas import CanonicalAsset, CanonicalFinding


class NetworkCSVAdapter(AdapterBase):
    slug = "network_csv"
    label = "Network/App CSV"
    supported_extensions = (".csv",)

    def detect(self, content: bytes, filename: str | None = None) -> bool:
        filename = filename or ""
        if filename.lower().endswith(".csv"):
            return True
        head = content[:256].decode("utf-8", errors="ignore").lower()
        return "id" in head and "severity" in head

    def parse(self, content: bytes) -> Iterable[Mapping[str, str]]:
        text = content.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)

    def map(self, parsed: Iterable[Mapping[str, str]]) -> Iterable[CanonicalFinding]:
        return list(self._iter_findings(parsed))

    def _iter_findings(self, rows: Iterable[Mapping[str, str]]) -> Iterator[CanonicalFinding]:
        for row in rows:
            if not row:
                continue
            finding_id = row.get("id") or row.get("finding_id")
            title = row.get("title") or row.get("summary")
            if not finding_id or not title:
                continue
            severity = (row.get("severity") or "").lower() or "unknown"
            cvss = self._safe_float(row.get("cvss"))
            epss = self._safe_float(row.get("epss"))
            kev = (row.get("kev") or "").strip().lower() in {"1", "true", "yes", "y"}
            effort_hours = self._safe_float(row.get("effort_hours"))
            asset_name = row.get("asset") or row.get("hostname")
            asset_kind = row.get("asset_kind") or row.get("type")
            asset = None
            if asset_name or asset_kind:
                asset = CanonicalAsset(name=asset_name, kind=asset_kind)

            yield CanonicalFinding(
                id=str(finding_id),
                title=title,
                description=row.get("description") or row.get("details"),
                severity=severity,
                cve=row.get("cve") or row.get("cve_id"),
                cvss=cvss,
                epss=epss,
                kev=kev,
                effort_hours=effort_hours,
                asset=asset,
                source=self.slug,
                tags=[tag.strip() for tag in (row.get("tags") or "").split("|") if tag.strip()],
            )

    @staticmethod
    def _safe_float(value: str | None) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except ValueError:
            return None


__all__ = ["NetworkCSVAdapter"]
