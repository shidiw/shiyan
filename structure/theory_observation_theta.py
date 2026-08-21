"""Observation-derived parameter map for the frozen Struct3D Unit.

For a finite 3-D observation X and a non-empty block A of its index universe,
this module freezes a semantic-free parameter map

    theta = T_X(A).

The defining invariant is the lexicographically sorted tuple of the observed
3-D coordinates belonging to A.  The signature is finite and is independent of
point indices, hence invariant under observation relabeling.  Because the
signature contains every observed coordinate exactly once, it is strictly
injective on geometric point-set blocks in a fixed observation coordinate
frame.  No semantic labels, primitive labels, thresholds, optimization,
or neural network are used.
"""

from __future__ import annotations

from typing import Mapping, Sequence, Tuple

from .theory_energy_model import Observation3D
from .theory_unit import StructuralUnit

Point = Tuple[float, float, float]
Signature = Tuple[Point, ...]


def observation_theta(observation: Observation3D, indices: Sequence[int]) -> Mapping[str, object]:
    """Return the frozen finite parameter theta=T_X(A).

    ``signature`` is the complete sorted coordinate multiset of the block.
    Since Observation3D is a finite set of indexed observations, partition
    blocks contain distinct indices; therefore the signature is a finite tuple
    with no information discarded.
    """
    block = tuple(sorted(set(int(i) for i in indices)))
    if not block:
        raise ValueError("Unit support must be non-empty")
    if len(block) != len(tuple(indices)):
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
    """Executable injectivity witness for the frozen theta map.

    Equal theta signatures imply equal observed geometric point sets.  The
    converse is exact by construction.
    """
    return theta_signature(u) == theta_signature(v)


def relabel_observation_unit(
    observation: Observation3D,
    indices: Sequence[int],
    permutation: Mapping[int, int],
) -> StructuralUnit:
    """Build the relabeled Unit; theta remains unchanged under index relabeling."""
    mapped = tuple(sorted(permutation[i] for i in indices))
    return observation_unit(observation, mapped)


__all__ = [
    "observation_theta",
    "observation_unit",
    "theta_signature",
    "theta_injective",
    "relabel_observation_unit",
]
