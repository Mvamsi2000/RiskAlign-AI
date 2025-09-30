"""CSV ingestion adapter for tabular network or vulnerability data."""
from __future__ import annotations

import csv
import io
from typing import Iterable, List

from server.schemas import AssetContext, CanonicalFinding

from .base import IngestAdapter


class NetworkCSVAdapter(IngestAdapter):
    """Parses CSV datasets such as vulnerability exports or network telemetry."""

    name = "network_csv"
    extensions = (".csv",)
    content_types = ("text/csv", "application/csv")

    def confidence(self, file_name: str, sample: bytes) -> float:
        text = sample[:256].decode("utf-8", errors="ignore").lower()
        if "," in text and ("cve" in text or "severity" in text or "label" in text):
            return 0.85
        return super().confidence(file_name, sample)

    def parse(self, file_name: str, data: bytes) -> Iterable[CanonicalFinding]:
        csv_text = self._ensure_unicode(data)
        reader = csv.DictReader(io.StringIO(csv_text))
        findings: List[CanonicalFinding] = []

        for index, row in enumerate(reader, start=1):
            label = (row.get("Label") or row.get("label") or "").strip().lower()
            if label in {"benign", "normal", "not malicious"}:
                continue

            cve = (row.get("CVE") or row.get("cve_id") or row.get("cve") or "").strip() or None
            title = (
                row.get("Title")
                or row.get("Name")
                or row.get("Vulnerability Name")
                or row.get("Attack")
                or row.get("Attack Category")
                or row.get("Threat")
                or "CSV Finding"
            )
            description = (
                row.get("Description")
                or row.get("Details")
                or row.get("Summary")
                or row.get("Notes")
                or "Parsed from CSV artifact"
            )
            severity = (
                row.get("Severity")
                or row.get("Risk")
                or row.get("Risk Level")
                or row.get("Threat Level")
                or label.upper() if label else None
            )
            cvss_value = row.get("CVSS") or row.get("CVSS Score") or row.get("cvss_score")
            cvss = float(cvss_value) if cvss_value else None
            epss_value = row.get("EPSS") or row.get("epss")
            epss = float(epss_value) if epss_value else None

            effort_value = row.get("Effort Hours") or row.get("effort")
            try:
                effort = float(effort_value) if effort_value else None
            except ValueError:
                effort = None

            asset_name = row.get("Asset") or row.get("Host") or row.get("Destination IP")
            asset = (
                AssetContext(
                    name=asset_name,
                    criticality=row.get("Criticality"),
                    exposure=row.get("Exposure") or row.get("Segment"),
                    data_sensitivity=row.get("Data Sensitivity"),
                )
                if asset_name or row.get("Criticality")
                else None
            )

            finding_id = row.get("Finding ID") or row.get("ID") or f"csv-{index}"
            tags = ["csv"]
            if label:
                tags.append(label.replace(" ", "-"))
            if row.get("Protocol"):
                tags.append(row["Protocol"].lower())

            findings.append(
                CanonicalFinding(
                    id=finding_id,
                    title=title,
                    description=description,
                    cve=cve,
                    severity=severity,
                    cvss=cvss,
                    epss=epss,
                    effort_hours=effort,
                    asset=asset,
                    tags=tags,
                )
            )
        return findings


__all__ = ["NetworkCSVAdapter"]
