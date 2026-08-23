"""Theory-safe structural primitives for Struct3D.

Frozen definitions:
    Structural Unit u_i = (G_i, theta_i)
    Structural World W = (U, R, Phi)
    Structural Graph G = (V, E)

The low-level ``Partition``/``select_minimizer`` API intentionally accepts an
explicit family for generic mathematical use and regression compatibility.
The closed raw-observation execution path is defined separately by
``ObservationDerivedContext`` and no longer relies on that explicit family as
an upstream theorem assumption.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

from .theory_unit import StructuralUnit

TheoryUnit = StructuralUnit


@dataclass(frozen=True)
class Partition:
    """A finite partition of an indexed observation universe."""

    units: Tuple[StructuralUnit, ...]
    universe: Tuple[int, ...]

    def __post_init__(self) -> None:
        universe = tuple(sorted(set(int(i) for i in self.universe)))
        if universe != self.universe:
            raise ValueError("Universe indices must be unique and sorted")
        if not universe:
            raise ValueError("Partition universe must be non-empty")

        covered = []
        for unit in self.units:
            if any(i not in universe for i in unit.indices):
                raise ValueError("A unit contains an index outside the universe")
            covered.extend(unit.indices)

        if len(covered) != len(set(covered)):
            raise ValueError("Partition units must be pairwise disjoint")
        if tuple(sorted(covered)) != universe:
            raise ValueError("Partition units must cover the complete universe")

    @property
    def is_partition(self) -> bool:
        return True


def evaluate_energy(partition: Partition, functional: Callable[[Partition], float]) -> float:
    """Evaluate a finite real-valued scalar functional."""
    value = float(functional(partition))
    if not math.isfinite(value):
        raise ValueError("Energy functional must return a finite real scalar")
    return value


def select_minimizer(
    candidates: Sequence[Partition],
    functional: Callable[[Partition], float],
) -> Partition:
    """Select an argmin from an explicit finite family.

    This is a generic theorem-facing primitive.  For raw observations, the
    candidate family should be obtained from ``ObservationDerivedContext``.
    """
    if not candidates:
        raise ValueError("At least one admissible partition is required")
    return min(candidates, key=lambda p: evaluate_energy(p, functional))
