"""Theory-safe mathematical core for Struct3D.

Frozen theory statements represented here:
    Structural Unit u_i = (G_i, theta_i)
    Partition Pi is a disjoint, complete family of units
    E is an externally supplied functional
    Pi* is selected from an explicit admissible candidate set

Primitive fitting, additive energy decompositions, graph thresholds and
minimum-size filters remain legacy engineering choices until justified by
the formal theory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class TheoryUnit:
    """A structural unit u=(G,theta).

    ``indices`` is the geometric support. ``attributes`` stores theta.
    ``primitive`` is optional metadata: a primitive explanation is not the
    definition of a Structural Unit.
    """

    indices: Tuple[int, ...]
    attributes: Mapping[str, Any] = field(default_factory=dict)
    primitive: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.indices:
            raise ValueError("A structural unit must be non-empty")
        if tuple(sorted(set(self.indices))) != self.indices:
            raise ValueError("Unit indices must be unique and sorted")
        if self.attributes is None:
            raise ValueError("Unit attributes cannot be None")

    @property
    def parameters(self) -> Mapping[str, Any]:
        """Backward-compatible name for structural attributes."""
        return self.attributes


@dataclass(frozen=True)
class Partition:
    """A finite partition of an indexed point set."""

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


def evaluate_energy(partition: Partition, functional: Callable[[Partition], float]) -> float:
    value = float(functional(partition))
    if value != value:
        raise ValueError("Energy functional returned NaN")
    return value


def select_minimizer(candidates: Sequence[Partition], functional: Callable[[Partition], float]) -> Partition:
    if not candidates:
        raise ValueError("At least one admissible partition is required")
    return min(candidates, key=lambda p: evaluate_energy(p, functional))
