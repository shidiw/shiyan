"""Theory-facing Structural Representation.

Frozen chain:
    W -> C(W) -> I(W) -> phi(W) in R^23.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .theory_invariant import structural_invariant
from .theory_representation_schema import (
    REPRESENTATION_DIM,
    validate_grouped_representation,
    group_slices,
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
        slices = group_slices()
        return {name: self.values[sl] for name, sl in slices.items()}


def _build_representation(values: Sequence[float]) -> StructuralRepresentation:
    return StructuralRepresentation(tuple(float(v) for v in values))


def represent(
    world: StructuralWorld,
    extractor: Callable[[StructuralWorld], Sequence[float]],
) -> StructuralRepresentation:
    return _build_representation(extractor(world))


def represent_canonical(
    world: StructuralWorld,
    extractor: Callable[[Any], Sequence[float]],
) -> StructuralRepresentation:
    return _build_representation(extractor(structural_invariant(world)))


__all__ = ["REPRESENTATION_DIM", "StructuralRepresentation", "represent", "represent_canonical"]
