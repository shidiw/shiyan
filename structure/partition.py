"""Theory-compliant partition interface.

A structural Unit is not defined by a primitive threshold alone.  The formal
pipeline is candidate partition -> structural energy -> stable partition ->
Unit.  This module provides the deterministic data model and leaves the
optimization policy explicit until the exact historical theory specifies it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class Partition:
    """A partition of point indices into disjoint non-empty regions."""

    regions: tuple[np.ndarray, ...]

    def __post_init__(self) -> None:
        cleaned = []
        for region in self.regions:
            arr = np.asarray(region, dtype=int).reshape(-1)
            if arr.size == 0:
                raise ValueError("Partition regions must be non-empty")
            cleaned.append(np.unique(arr))
        object.__setattr__(self, "regions", tuple(cleaned))


class StablePartitionSolver:
    """Select a minimum-energy candidate partition.

    This is intentionally a small, exact interface rather than a hidden
    heuristic clustering algorithm.  For a candidate set P, the formal rule
    is argmin_P E(P).  Candidate generation and scalable optimization belong
    to separate modules and must not change the definition of stability.
    """

    def select(
        self,
        candidates: Sequence[Partition],
        energy: Callable[[Partition], float],
    ) -> tuple[Partition, float]:
        if not candidates:
            raise ValueError("At least one candidate partition is required")

        values = [float(energy(p)) for p in candidates]
        best = int(np.argmin(values))
        return candidates[best], values[best]


def partition_energy(
    partition: Partition,
    unit_energy: Callable[[np.ndarray], float],
) -> float:
    """Sum candidate-region energies without adding an undocumented term."""
    return float(sum(unit_energy(region) for region in partition.regions))
