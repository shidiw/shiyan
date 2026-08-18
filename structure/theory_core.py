"""Minimal theory-facing core for Struct3D.

This module deliberately implements only statements that are safe to make
without inventing a new energy decomposition or partition heuristic.

Current status:
- a StructuralUnit is a candidate subset plus its primitive parameters;
- a partition is a finite family of non-empty, pairwise-disjoint subsets
  whose union is the represented point set;
- an energy is an externally supplied functional on candidates/partitions.

No additive energy, threshold, minimum component size, or relation rule is
silently promoted to theory here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Hashable, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class TheoryUnit:
    """A mathematical candidate structural unit.

    ``indices`` identifies the subset of the ambient point set. ``primitive``
    and ``parameters`` are descriptors; they do not by themselves assert
    optimality.
    """

    indices: Tuple[int, ...]
    primitive: str
    parameters: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.indices:
            raise ValueError("A structural unit must be non-empty")
        if tuple(sorted(set(self.indices))) != self.indices:
            raise ValueError("Unit indices must be unique and sorted")
        if not self.primitive:
            raise ValueError("A structural unit requires a primitive label")


@dataclass(frozen=True)
class Partition:
    """A partition of a finite indexed point set."""

    units: Tuple[TheoryUnit, ...]
    universe: Tuple[int, ...]

    def __post_init__(self) -> None:
        universe = tuple(sorted(set(self.universe)))
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


def evaluate_energy(
    partition: Partition,
    functional: Callable[[Partition], float],
) -> float:
    """Evaluate an externally defined partition functional.

    The function intentionally does not prescribe its algebraic form.
    """
    value = float(functional(partition))
    if value != value:  # NaN
        raise ValueError("Energy functional returned NaN")
    return value


def select_minimizer(
    candidates: Sequence[Partition],
    functional: Callable[[Partition], float],
) -> Partition:
    """Select a minimum-energy candidate from an explicit admissible set.

    This is the operational form of argmin once the admissible set and
    functional have been supplied by the theory. It does not create either.
    """
    if not candidates:
        raise ValueError("At least one admissible partition is required")
    return min(candidates, key=lambda p: evaluate_energy(p, functional))
