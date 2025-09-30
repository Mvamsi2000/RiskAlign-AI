"""Lightweight semantic store backed by an in-memory similarity search."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np

from server.schemas import CanonicalFinding

_DIMENSION = 256


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in text.split() if token]


def _embed(text: str) -> np.ndarray:
    tokens = _tokenize(text)
    vector = np.zeros(_DIMENSION, dtype=np.float32)
    for token in tokens:
        index = hash(token) % _DIMENSION
        vector[index] += 1.0
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


@dataclass
class VectorIndex:
    matrix: np.ndarray
    ids: List[str]

    def search(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        query = _embed(text)
        if not self.ids:
            return []
        scores = self.matrix @ query
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.ids[i], float(scores[i])) for i in top_indices if scores[i] > 0]


def build_vector_index(findings: Iterable[CanonicalFinding]) -> VectorIndex:
    ids: List[str] = []
    vectors: List[np.ndarray] = []
    for finding in findings:
        ids.append(finding.id)
        text = " ".join(filter(None, [finding.title, finding.description or "", " ".join(finding.tags or [])]))
        vectors.append(_embed(text))
    matrix = np.vstack(vectors) if vectors else np.zeros((0, _DIMENSION), dtype=np.float32)
    return VectorIndex(matrix=matrix, ids=ids)


__all__ = ["VectorIndex", "build_vector_index"]
