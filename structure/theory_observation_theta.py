"""Observation-derived parameter map for the frozen Struct3D Unit.

For a finite 3-D observation X and a non-empty block A of its index universe,
this module freezes a semantic-free parameter map theta=T_X(A).

The defining invariant is the lexicographically sorted tuple of the observed
3-D coordinates belonging to A. The signature is finite and independent of
point indices, hence invariant under observation relabeling. For a *simple*
observation (distinct observed coordinates), it is strictly injective on
geometric blocks. No semantic labels, primitive labels, thresholds,
optimization, or neural network are used.
"""

from __future__ import annotations

from typing import Mapping, Sequence, Tuple

from .theory_energy_model import Observation3D
from .theory_unit import StructuralUnit

Point = Tuple[float, float, float]
Signature = Tuple[Point, ...]


def _validate_simple_observation(observation: Observation3D) -> None:
    """The strict-injectivity theorem requires a simple finite observation."""
    if len(set(observation.points)) != len(observation.points):
        raise ValueError("Strict theta injectivity requires distinct observed coordinates")


def observation_theta(observation: Observation3D, indices: Sequence[int]) -> Mapping[str, object]:
    """Return the frozen finite parameter theta=T_X(A)."""
    _validate_simple_observation(observation)
    raw = tuple(int(i) for i in indices)
    block = tuple(sorted(set(raw)))
    if not block:
        raise ValueError("Unit support must be non-empty")
    if len(block) != len(raw):
        raise ValueError("Unit support indices must be unique")
    if any(i < 0 or i >= len(observation.points) for i in block):
        raise ValueError("Unit support lies outside the observation")

    signature: Signature = tuple(sorted(observation.points[i] for i in block))
    centroid = tuple(sum(p[d] for p in signature) / len(signature) for d in range(3))
    return {
        "cardinality": len(signature),
        "centroid": centroid,
        "signature": signature,
    }


def observation_unit(observation: Observation3D, indices: Sequence[int]) -> StructuralUnit:
    """Construct u=(A,T_X(A)) directly from a finite observation."""
    block = tuple(sorted(set(int(i) for i in indices)))
    return StructuralUnit(indices=block, attributes=observation_theta(observation, block))


def theta_signature(unit: StructuralUnit) -> Signature:
    """Extract the complete finite geometric signature from a Unit."""
    value = unit.attributes.get("signature")
    if not isinstance(value, tuple):
        raise ValueError("Unit does not contain an observation-derived signature")
    return value  # type: ignore[return-value]


def theta_injective(u: StructuralUnit, v: StructuralUnit) -> bool:
    """Return whether two Units have the same frozen theta signature."""
    return theta_signature(u) == theta_signature(v)


def relabel_observation_unit(
    observation: Observation3D,
    indices: Sequence[int],
    permutation: Mapping[int, int],
) -> StructuralUnit:
    """Build a relabeled Unit; theta is unchanged when X is relabeled consistently."""
    n = len(observation.points)
    if set(permutation) != set(range(n)) or set(permutation.values()) != set(range(n)):
        raise ValueError("Permutation must be a bijection of the observation universe")
    mapped = tuple(sorted(permutation[i] for i in indices))
    relabeled_points = [None] * n
    for old, new in permutation.items():
        relabeled_points[new] = observation.points[old]
    relabeled = Observation3D(points=tuple(relabeled_points))
    return observation_unit(relabeled, mapped)


__all__ = [
    "observation_theta",
    "observation_unit",
    "theta_signature",
    "theta_injective",
    "relabel_observation_unit",
]
