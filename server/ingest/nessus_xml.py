"""Nessus XML ingestion adapter."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Iterable, List

from server.schemas import CanonicalFinding

from .base import IngestAdapter


class NessusXMLAdapter(IngestAdapter):
    """Parses Nessus v2 XML exports."""

    name = "nessus_xml"
    extensions = (".nessus", ".xml")
    content_types = ("application/xml", "text/xml")

    def confidence(self, file_name: str, sample: bytes) -> float:
        text = sample[:256].decode("utf-8", errors="ignore").lower()
        if "nessusclientdata_v2" in text:
            return 0.95
        return super().confidence(file_name, sample)

    def parse(self, file_name: str, data: bytes) -> Iterable[CanonicalFinding]:
        xml_text = self._ensure_unicode(data)
        try:
            tree = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise ValueError("Invalid Nessus XML document") from exc

        findings: List[CanonicalFinding] = []
        for item in tree.findall(".//ReportItem"):
            plugin_id = item.get("pluginID") or "nessus"
            finding_id = f"nessus-{plugin_id}"
            title = item.get("pluginName") or item.findtext("pluginName") or "Nessus Finding"
            description = item.findtext("description") or ""
            cve = item.get("cve") or item.findtext("cve")
            severity = item.get("severity") or item.findtext("risk_factor")
            cvss_text = item.get("cvss_base_score") or item.findtext("cvss_base_score")
            remediation = item.findtext("solution")
            references = [ref.text for ref in item.findall("see_also")] if item.findall("see_also") else []

            cvss = float(cvss_text) if cvss_text else None

            findings.append(
                CanonicalFinding(
                    id=finding_id,
                    title=title,
                    description=description,
                    cve=cve,
                    severity=severity,
                    cvss=cvss,
                    remediation=remediation,
                    references=references,
                    tags=["nessus"],
                )
            )
        return findings


__all__ = ["NessusXMLAdapter"]
