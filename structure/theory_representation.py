"""Theory-facing Structural Representation.

Frozen statement:
    phi(W) in R^23

The supplied theory freezes the seven coordinate groups but does not freeze a
unique numerical estimator for every statistic. Consequently ``represent``
accepts an explicit extractor and validates the frozen coordinate contract;
it does not silently invent feature formulas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .theory_representation_schema import (
    REPRESENTATION_DIM,
    REPRESENTATION_GROUPS,
    group_slices,
    validate_grouped_representation,
)
from .theory_world import StructuralWorld


@dataclass(frozen=True)
class StructuralRepresentation:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        validate_grouped_representation(self.values)

    def as_tuple(self) -> tuple[float, ...]:
        return tuple(float(v) for v in self.values)

    @property
    def groups(self):
        """Return the frozen v4.0 group slices, without changing values."""
        slices = group_slices()
        return {name: self.values[sl] for name, sl in slices.items()}


def represent(
    world: StructuralWorld,
    extractor: Callable[[StructuralWorld], Sequence[float]],
) -> StructuralRepresentation:
    """Apply an explicitly supplied v4.0 feature extractor.

    The extractor is an implementation dependency, not a hidden theorem.
    In particular, this function does not claim that arbitrary extractors are
    relabeling-invariant. An invariant extractor must be tested separately.
    """
    values = tuple(float(v) for v in extractor(world))
    return StructuralRepresentation(values)
