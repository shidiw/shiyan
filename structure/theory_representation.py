"""Theory-facing Structural Representation.

Frozen statement:
    phi(W) in R^23

The theory freezes the seven coordinate groups but does not freeze a unique
numerical estimator for every statistic. Therefore ``represent`` accepts an
explicit extractor and validates the frozen coordinate contract; it does not
silently invent feature formulas.

For an invariance claim, use ``represent_canonical``. It applies the extractor
to the exact canonical form C(W), so relabeling invariance follows from the
canonical-form contract rather than from an unproved property of an arbitrary
world-level extractor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .theory_canonical import canonical_form
from .theory_representation_schema import group_slices, validate_grouped_representation
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


def _build_representation(values: Sequence[float]) -> StructuralRepresentation:
    return StructuralRepresentation(tuple(float(v) for v in values))


def represent(
    world: StructuralWorld,
    extractor: Callable[[StructuralWorld], Sequence[float]],
) -> StructuralRepresentation:
    """Apply an explicitly supplied v4.0 feature extractor.

    This function makes no invariance claim about an arbitrary extractor.
    """
    return _build_representation(extractor(world))


def represent_canonical(
    world: StructuralWorld,
    extractor: Callable[[Any], Sequence[float]],
) -> StructuralRepresentation:
    """Represent a world through its exact canonical form.

    The extractor receives only C(W), not the original unit labels. Therefore
    the composition extractor(C(W)) is invariant under relabelings whenever
    canonical_form satisfies its exact relabeling-invariance contract.
    """
    return _build_representation(extractor(canonical_form(world)))
