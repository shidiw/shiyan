"""Theory-safe structural primitives for Struct3D.

Frozen definitions from the mathematical specification:
    Structural Unit u_i = (G_i, theta_i)
    Structural World W = (U, R, Phi)
    Structural Graph G = (V, E)

The implementation uses one StructuralUnit type throughout the theory-facing
layer. ``TheoryUnit`` is retained only as a compatibility alias; there are not
two different mathematical Unit classes.

The specification does not freeze a unique energy functional or a construction
of admissible partitions from raw observations. Partition discovery and energy
therefore remain explicit external inputs.
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
    """Evaluate an externally supplied scalar functional.

    The finite-selection theorem requires real-valued (not NaN/inf) energy on
    every candidate.  Enforcing that requirement here keeps the generic core
    consistent with Stage 2F and prevents a non-finite value from silently
    becoming an argmin witness.
    """
    value = float(functional(partition))
    if not math.isfinite(value):
        raise ValueError("Energy functional must return a finite real scalar")
    return value


def select_minimizer(
    candidates: Sequence[Partition],
    functional: Callable[[Partition], float],
) -> Partition:
    """Select an argmin from an explicit finite admissible set."""
    if not candidates:
        raise ValueError("At least one admissible partition is required")
    return min(candidates, key=lambda p: evaluate_energy(p, functional))
