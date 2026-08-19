"""Explicit admissible-partition family boundary for Struct3D.

The frozen mathematical theory requires an admissible family A(X) before an
optimal partition can be selected.  The current source theory does not freeze
the construction X -> A(X), so this module deliberately represents A(X) as an
external finite input rather than inventing a discovery heuristic.

This is a contract boundary, not a new definition of what makes a partition
admissible from raw observations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .theory_core import Partition, evaluate_energy


@dataclass(frozen=True)
class AdmissiblePartitionFamily:
    """A non-empty finite family of partitions sharing one observation domain.

    The family is supplied by the caller.  No geometry threshold, connected
    component rule, primitive classifier, or legacy energy is used to construct
    it here.
    """

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
        """Return one argmin over the supplied finite admissible family."""
        return min(
            self.partitions,
            key=lambda partition: evaluate_energy(partition, functional),
        )


def select_admissible_minimizer(family: AdmissiblePartitionFamily, functional) -> Partition:
    """Select an argmin from an explicitly supplied admissible family."""
    return family.minimizer(functional)
