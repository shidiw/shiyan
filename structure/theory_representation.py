"""Theory-facing Structural Representation.

Frozen chain:
    W -> C(W) -> I(W) -> phi(W) in R^23.

``represent`` is an explicitly supplied world-level extractor and makes no
invariance claim. ``represent_canonical`` uses the frozen invariant object
I(W)=C(W), so any invariance claim is delegated to the exact canonical layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .theory_invariant import structural_invariant
from .theory_representation_schema import validate_grouped_representation, group_slices
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
    """Compute phi(W) from the frozen structural invariant I(W)."""
    return _build_representation(extractor(structural_invariant(world)))
