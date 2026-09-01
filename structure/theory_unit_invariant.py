"""Complete observation-aware invariant for Structural Units.

For X=(x_0,...,x_{n-1}) and u=(G,theta), define

    Can_U^X(u) = ( multiset{ x_i : i in G }, Freeze(theta) ).

The point coordinates are sorted lexicographically, so this is a finite,
deterministic canonical representative. The historical ``primitive`` field is
excluded because the frozen mathematical Unit is u=(G,theta).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Tuple

from .theory_core import StructuralUnit

Point = Tuple[float, float, float]


def _freeze(value: Any):
    if isinstance(value, Mapping):
        return tuple(sorted((repr(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(v) for v in value), key=repr))
    try:
        hash(value)
    except TypeError:
        return repr(value)
    return value


def _point_key(point: Point) -> Point:
    return tuple(float(v) for v in point)  # type: ignore[return-value]


def Can_U(unit: StructuralUnit, observation):
    """Return the frozen complete invariant ``Can_U^X(u)``."""
    n = len(observation.points)
    if not unit.indices:
        raise ValueError("Structural Unit support must be non-empty")
    if any(i < 0 or i >= n for i in unit.indices):
        raise ValueError("Unit support lies outside the observation")
    points = tuple(sorted((_point_key(observation.points[i]) for i in unit.indices)))
    return (points, _freeze(unit.attributes))


def unit_equivalent_X(first: StructuralUnit, second: StructuralUnit, observation) -> bool:
    """Test the Unit quotient relation when both Units live in one X."""
    return Can_U(first, observation) == Can_U(second, observation)


def unit_equivalent_between_observations(
    first: StructuralUnit,
    first_observation,
    second: StructuralUnit,
    second_observation,
) -> bool:
    """Compare Units living in two observations through their canonical forms.

    This is the correct cross-observation quotient statement. A one-observation
    predicate cannot infer the original coordinate system of the other Unit.
    """
    return Can_U(first, first_observation) == Can_U(second, second_observation)


def relabel_unit(unit: StructuralUnit, permutation: Sequence[int]) -> StructuralUnit:
    """Transport a Unit through ``x'_j=x_{permutation[j]}`` using the inverse map."""
    if len(permutation) == 0:
        raise ValueError("permutation must be non-empty")
    mapping = tuple(int(v) for v in permutation)
    if tuple(sorted(mapping)) != tuple(range(len(mapping))):
        raise ValueError("permutation must contain each index exactly once")
    if any(i < 0 or i >= len(mapping) for i in unit.indices):
        raise ValueError("Unit support lies outside permutation domain")
    inverse = {old: new for new, old in enumerate(mapping)}
    return StructuralUnit(tuple(sorted(inverse[i] for i in unit.indices)), dict(unit.attributes), unit.primitive)


def can_u_is_invariant_under_relabeling(unit: StructuralUnit, observation, permutation: Sequence[int]) -> bool:
    """Check finite observation quotient invariance under relabeling."""
    if len(permutation) != len(observation.points):
        raise ValueError("permutation must match the observation cardinality")
    observation_type = type(observation)
    relabeled_observation = observation_type(tuple(observation.points[i] for i in permutation))
    relabeled_unit = relabel_unit(unit, permutation)
    return Can_U(unit, observation) == Can_U(relabeled_unit, relabeled_observation)


__all__ = [
    "Can_U",
    "unit_equivalent_X",
    "unit_equivalent_between_observations",
    "relabel_unit",
    "can_u_is_invariant_under_relabeling",
]
