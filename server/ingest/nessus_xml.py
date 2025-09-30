from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Iterable, Iterator, Optional

from .base import AdapterBase
from ..schemas import CanonicalAsset, CanonicalFinding

_SEVERITY_MAP = {
    "0": "informational",
    "1": "low",
    "2": "medium",
    "3": "high",
    "4": "critical",
}


def _safe_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class NessusXMLAdapter(AdapterBase):
    slug = "nessus_xml"
    label = "Tenable Nessus XML"
    supported_extensions = (".nessus", ".xml")

    def detect(self, content: bytes, filename: str | None = None) -> bool:
        filename = filename or ""
        lowered = filename.lower()
        if any(lowered.endswith(ext) for ext in self.supported_extensions):
            return True
        # Inspect the first chunk for the Nessus XML signature.
        head = content[:512].decode("utf-8", errors="ignore")
        return "NessusClientData_v2" in head

    def parse(self, content: bytes) -> ET.Element:
        return ET.fromstring(content)

    def map(self, parsed: ET.Element) -> Iterable[CanonicalFinding]:
        return list(self._iter_findings(parsed))

    def _iter_findings(self, root: ET.Element) -> Iterator[CanonicalFinding]:
        report = root.find("Report")
        if report is None:
            return iter(())
        for host in report.findall("ReportHost"):
            host_name = host.get("name") or host.findtext("HostName")
            host_ip = host.findtext("HostIP")
            asset = CanonicalAsset(name=host_name, ip_address=host_ip)
            for item in host.findall("ReportItem"):
                plugin_id = item.get("pluginID") or item.get("plugin_id") or "plugin"
                title = item.get("pluginName") or item.findtext("plugin_name") or "Nessus finding"
                description = item.findtext("description")
                cve = item.get("cve") or item.findtext("cve")
                cvss = _safe_float(item.get("cvssBaseScore") or item.findtext("cvss_base_score"))
                severity_code = item.get("severity") or item.get("severity_id")
                severity = _SEVERITY_MAP.get(severity_code or "", "unknown")
                observed = item.get("firstSeen") or item.findtext("first_discovered")
                observed_at = None
                if observed:
                    try:
                        observed_at = datetime.fromisoformat(observed)
                    except ValueError:
                        observed_at = None
                raw = {
                    "plugin_id": plugin_id,
                    "plugin_family": item.get("pluginFamily"),
                    "plugin_type": item.get("pluginType"),
                }

                yield CanonicalFinding(
                    id=f"{plugin_id}-{host_name or host_ip or 'host'}",
                    title=title,
                    description=description,
                    severity=severity,
                    cve=cve,
                    cvss=cvss,
                    asset=asset,
                    observed_at=observed_at,
                    source=self.slug,
                    raw=raw,
                )


__all__ = ["NessusXMLAdapter"]
