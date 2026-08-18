"""Theory-facing Structural Representation.

The frozen v4.0 target is phi(W) in R^23. This module enforces the dimension
and provenance without inventing how each of the 23 statistics is computed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .theory_world import StructuralWorld


REPRESENTATION_DIM = 23


@dataclass(frozen=True)
class StructuralRepresentation:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) != REPRESENTATION_DIM:
            raise ValueError(f"Struct3D v4.0 representation must have {REPRESENTATION_DIM} dimensions")
        if not all(float(v) == float(v) for v in self.values):
            raise ValueError("representation cannot contain NaN")

    def as_tuple(self) -> tuple[float, ...]:
        return tuple(float(v) for v in self.values)


def represent(world: StructuralWorld, extractor: Callable[[StructuralWorld], Sequence[float]]) -> StructuralRepresentation:
    """Apply an explicitly supplied v4.0 feature extractor."""
    values = tuple(float(v) for v in extractor(world))
    return StructuralRepresentation(values)
