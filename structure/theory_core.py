"""Theory-safe structural primitives for Struct3D.

The uploaded Struct3D mathematical specification freezes:
    Structural Unit u_i = (G_i, theta_i)
    Structural World W = (U, R, Phi)
    Structural Graph G = (V, E)

It does NOT freeze a specific energy functional or a specific construction of
an admissible partition from raw points. ``Partition`` therefore remains a
mathematically valid finite partition container, but its discovery mechanism
is deliberately external/provisional until an energy/partition theorem is
formally added to the specification.

Primitive fitting, additive energy decompositions, graph thresholds and
minimum-size filters remain legacy engineering choices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class TheoryUnit:
    """Structural Unit u=(G, theta), represented by point support and attributes."""

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
    """A finite partition container over an indexed observation universe.

    This class formalizes partition validity only. It does not claim that the
    current Struct3D theory specifies how candidate partitions are generated
    or which energy must select one.
    """

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
    """Evaluate an externally supplied scalar functional.

    This is an interface for later formalization, not a claim that the
    supplied Struct3D specification already defines a unique E.
    """
    value = float(functional(partition))
    if value != value:
        raise ValueError("Energy functional returned NaN")
    return value


def select_minimizer(candidates: Sequence[Partition], functional: Callable[[Partition], float]) -> Partition:
    """Select an argmin from an explicit finite candidate set.

    This implements the generic optimization operator used by the current
    engineering scaffold. It must not be read as a theorem that the uploaded
    Struct3D specification already defines Pi*=argmin E(Pi).
    """
    if not candidates:
        raise ValueError("At least one admissible partition is required")
    return min(candidates, key=lambda p: evaluate_energy(p, functional))
