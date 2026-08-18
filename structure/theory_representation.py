"""Theory-facing Structural Representation.

Frozen statement: phi(W) in R^23.

The numerical extractor is not itself a theorem. Two paths remain explicit:
``represent`` applies a world-level extractor without an invariance claim;
``represent_canonical`` applies an extractor only to C(W).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .theory_canonical import canonical_form
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
        slices = group_slices()
        return {name: self.values[sl] for name, sl in slices.items()}


def _build_representation(values: Sequence[float]) -> StructuralRepresentation:
    return StructuralRepresentation(tuple(float(v) for v in values))


def represent(
    world: StructuralWorld,
    extractor: Callable[[StructuralWorld], Sequence[float]],
) -> StructuralRepresentation:
    """Apply an explicit world-level extractor; no invariance is claimed."""
    return _build_representation(extractor(world))


def represent_canonical(
    world: StructuralWorld,
    extractor: Callable[[Any], Sequence[float]],
) -> StructuralRepresentation:
    """Compute phi(W) through the exact canonical form C(W)."""
    return _build_representation(extractor(canonical_form(world)))
