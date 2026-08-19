"""Theory-facing Structural Representation.

Frozen mathematical chain::

    W -> C(W) -> I(W) -> phi(W) in R^23.

Important boundary:
    The current theory freezes the 23-dimensional coordinate schema, but does
    not freeze numerical formulas for the seven coordinate groups. Therefore
    numeric coordinates must always come from an explicit caller-supplied
    extractor. This module never invents statistics and never treats an
    arbitrary extractor as invariant or information-complete.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .theory_invariant import structural_invariant
from .theory_representation_schema import (
    REPRESENTATION_DIM,
    group_slices,
    validate_grouped_representation,
)
from .theory_world import StructuralWorld


RepresentationExtractor = Callable[[Any], Sequence[float]]


@dataclass(frozen=True)
class StructuralRepresentation:
    """A validated point of the frozen representation space ``R^23``.

    Validation here establishes only membership in the frozen coordinate
    contract. It does not establish relabeling invariance, injectivity, or
    structural completeness.
    """

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
    """Materialize coordinates without supplying any unstated feature formula."""
    return StructuralRepresentation(tuple(float(v) for v in values))


def represent(
    world: StructuralWorld,
    extractor: RepresentationExtractor,
) -> StructuralRepresentation:
    """Apply an explicit extractor directly to ``world``.

    This is intentionally a low-level engineering boundary. Calling this
    function does *not* certify that ``extractor`` is relabeling-invariant or
    that it is the mathematical Struct3D representation. Those properties
    require a separately specified extractor and separate validation.
    """
    return _build_representation(extractor(world))


def represent_canonical(
    world: StructuralWorld,
    extractor: RepresentationExtractor,
) -> StructuralRepresentation:
    """Apply an explicit extractor to the frozen invariant ``I(W)=C(W)``.

    The canonical input removes dependence on the current finite unit-label
    ordering. This establishes the correct *input path* for a proposed
    invariant extractor, but does not by itself prove any stronger property
    such as injectivity or information completeness.
    """
    invariant = structural_invariant(world)
    return _build_representation(extractor(invariant))


__all__ = [
    "REPRESENTATION_DIM",
    "RepresentationExtractor",
    "StructuralRepresentation",
    "represent",
    "represent_canonical",
]
