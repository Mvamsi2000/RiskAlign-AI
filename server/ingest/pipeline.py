from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Tuple

from ..core.tenancy import output_path
from ..enrich.epss import lookup_epss
from ..enrich.kev import is_kev
from ..schemas import CanonicalFinding, MCPEnvelope
from .auto_detect import detect_adapter

_CANONICAL_DIR = "canonical"


@dataclass
class IngestStats:
    detected: str
    adapter_label: str
    count: int
    accepted: int
    rejected: int
    path: Path
    sample: List[Mapping[str, Any]]


class IngestError(RuntimeError):
    """Raised when ingestion fails due to invalid input."""


def _prepare_finding(finding: CanonicalFinding) -> CanonicalFinding:
    payload = finding.model_dump()
    signals = payload.setdefault("signals", {})

    cve = payload.get("cve")
    if isinstance(cve, str) and cve:
        epss_score = lookup_epss(cve)
        if epss_score is not None:
            payload["epss"] = epss_score
            signals["epss"] = epss_score
        if is_kev(cve):
            payload["kev"] = True
            signals["kev"] = True

    return CanonicalFinding.model_validate(payload)


def _ensure_list(value: Iterable[CanonicalFinding] | CanonicalFinding) -> Iterable[CanonicalFinding]:
    if isinstance(value, CanonicalFinding):
        return [value]
    return value


def run_ingest_pipeline(content: bytes, filename: str, namespace: str) -> IngestStats:
    """Detect, parse and persist a canonical findings batch."""

    adapter = detect_adapter(content, filename)
    if adapter is None:
        raise IngestError("Unable to detect ingestion adapter for the provided file")

    parsed = adapter.parse(content)
    canonical_iterable = adapter.map(parsed)

    count = 0
    accepted = 0
    rejected = 0
    envelopes: List[MCPEnvelope] = []
    samples: List[Mapping[str, Any]] = []

    for candidate in _ensure_list(canonical_iterable):
        count += 1
        try:
            finding = candidate
            if not isinstance(finding, CanonicalFinding):
                finding = CanonicalFinding.model_validate(candidate)
            enriched = _prepare_finding(finding)
        except Exception:
            rejected += 1
            continue

        accepted += 1
        envelopes.append(
            MCPEnvelope(
                namespace=namespace,
                adapter=adapter.slug,
                received_at=datetime.now(timezone.utc),
                data=enriched,
                meta={"adapter_label": adapter.label},
            )
        )
        if len(samples) < 3:
            samples.append(enriched.model_dump())

    if not envelopes:
        raise IngestError("No valid findings were produced from the uploaded file")

    namespace_dir = output_path(namespace) / _CANONICAL_DIR
    namespace_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    target = namespace_dir / f"{timestamp}.jsonl"

    with target.open("w", encoding="utf-8") as handle:
        for envelope in envelopes:
            handle.write(json.dumps(envelope.model_dump(mode="json")) + "\n")

    return IngestStats(
        detected=adapter.slug,
        adapter_label=adapter.label,
        count=count,
        accepted=accepted,
        rejected=rejected,
        path=target,
        sample=samples,
    )


def list_canonical_batches(namespace: str) -> List[Tuple[str, Path]]:
    """Return available canonical batch filenames sorted by recency."""

    namespace_dir = output_path(namespace) / _CANONICAL_DIR
    if not namespace_dir.exists():
        return []

    files = [path for path in namespace_dir.glob("*.jsonl") if path.is_file()]
    files.sort(reverse=True)
    return [(path.name, path) for path in files]


def load_canonical_batch(namespace: str, batch_name: str | None = None) -> Tuple[List[Mapping[str, Any]], str | None]:
    """Load canonical findings for the requested batch."""

    batches = list_canonical_batches(namespace)
    if not batches:
        return [], None

    target_name, path = batches[0]
    if batch_name is not None:
        for candidate_name, candidate_path in batches:
            if candidate_name == batch_name:
                target_name, path = candidate_name, candidate_path
                break

    findings: List[Mapping[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            data = payload.get("data")
            if isinstance(data, Mapping):
                findings.append(dict(data))

    return findings, target_name


def load_latest_canonical(namespace: str) -> Tuple[List[Mapping[str, Any]], str | None]:
    """Convenience wrapper returning the most recent canonical batch."""

    return load_canonical_batch(namespace, None)


__all__ = [
    "IngestStats",
    "IngestError",
    "run_ingest_pipeline",
    "list_canonical_batches",
    "load_canonical_batch",
    "load_latest_canonical",
]
