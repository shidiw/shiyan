"""Theory-facing stability and minimality boundary for Struct3D.

The preserved Struct3D theory requires stability against an allowed structural
perturbation, but it does not freeze the perturbation family itself.  This
module therefore makes the missing mathematical inputs explicit instead of
inventing a merge rule, threshold, or stability score.

For an explicitly supplied candidate A, neighborhood N(A), and scalar energy
E, local stability is the predicate

    Stable(A; N, E) iff E(A) <= E(B) for every B in N(A).

Minimality is defined relative to an explicitly supplied family of proper
subcandidates:

    MinimalStable(A) iff Stable(A) and no proper subcandidate is stable.

These are executable predicates over explicit inputs.  They are not a claim
that the preserved historical theory has already proved a unique
Unit-emergence theorem.  In particular, no fixed threshold and no pairwise
merge formula is introduced here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Generic, Sequence, Tuple, TypeVar

T = TypeVar("T")
Energy = Callable[[T], float]


@dataclass(frozen=True)
class StabilityNeighborhood(Generic[T]):
    """Explicit alternatives against which one candidate is tested."""

    alternatives: Tuple[T, ...]

    def __post_init__(self) -> None:
        if not self.alternatives:
            raise ValueError("A stability neighborhood must contain at least one alternative")


def _finite_energy(candidate: T, energy: Energy[T]) -> float:
    value = float(energy(candidate))
    if not math.isfinite(value):
        raise ValueError("Stability energy must be a finite real scalar")
    return value


def is_locally_stable(
    candidate: T,
    neighborhood: StabilityNeighborhood[T],
    energy: Energy[T],
) -> bool:
    """Return whether no explicitly supplied alternative lowers the energy."""
    candidate_energy = _finite_energy(candidate, energy)
    return all(candidate_energy <= _finite_energy(other, energy) for other in neighborhood.alternatives)


def is_minimal_stable(
    candidate: T,
    neighborhood: StabilityNeighborhood[T],
    proper_stable_subcandidates: Sequence[T],
    energy: Energy[T],
) -> bool:
    """Test stability plus absence of an explicitly supplied stable subcandidate.

    The caller supplies the proper-subcandidate relation by construction; this
    function does not infer containment, connectivity, or splitting from raw
    geometry.
    """
    if not is_locally_stable(candidate, neighborhood, energy):
        return False

    for subcandidate in proper_stable_subcandidates:
        sub_neighborhood = StabilityNeighborhood((candidate,))
        if is_locally_stable(subcandidate, sub_neighborhood, energy):
            return False
    return True


__all__ = [
    "StabilityNeighborhood",
    "is_locally_stable",
    "is_minimal_stable",
]
