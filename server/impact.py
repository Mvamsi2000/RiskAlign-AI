"""Impact modeling for RiskAlign-AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ImpactEstimate:
    """Simple data structure for capturing impact calculations."""

    category: str
    likelihood: float
    severity: float

    @property
    def risk(self) -> float:
        """Return the overall risk value using a basic multiplication model."""
        return self.likelihood * self.severity


def normalize(value: float, *, upper: float = 5.0) -> float:
    """Normalize a value to the range 0-1 based on an expected upper bound."""
    if upper <= 0:
        return 0.0
    return max(0.0, min(value / upper, 1.0))


__all__ = [
    "ImpactEstimate",
    "normalize",
]
