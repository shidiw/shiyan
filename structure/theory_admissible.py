"""Generic explicit admissible-partition family boundary for Struct3D.

This module remains as a low-level compatibility interface for callers that
already possess a finite admissible family. It is no longer the raw-observation
formation boundary: the closed path defines ``A_max(X)`` and ``Gamma(X)`` in
``theory_candidates.py`` and exposes them through ``ObservationDerivedContext``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .theory_core import Partition, evaluate_energy


@dataclass(frozen=True)
class AdmissiblePartitionFamily:
    """A non-empty finite family of partitions sharing one universe."""

    partitions: Tuple[Partition, ...]

    def __post_init__(self) -> None:
        if not self.partitions:
            raise ValueError("Admissible partition family must be non-empty")
        universe = self.partitions[0].universe
        if any(partition.universe != universe for partition in self.partitions):
            raise ValueError("All admissible partitions must share one universe")

    @property
    def universe(self) -> Tuple[int, ...]:
        return self.partitions[0].universe

    def minimizer(self, functional) -> Partition:
        return min(self.partitions, key=lambda partition: evaluate_energy(partition, functional))


def select_admissible_minimizer(family: AdmissiblePartitionFamily, functional) -> Partition:
    return family.minimizer(functional)
