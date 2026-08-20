"""Theory-facing stability and minimality boundary for Struct3D.

The preserved Struct3D theory requires stability against an allowed structural
perturbation, but it does not freeze the perturbation family itself. This module
therefore makes the missing mathematical inputs explicit instead of inventing a
merge rule, threshold, or stability score.

For an explicitly supplied candidate A, neighborhood N(A), and scalar energy E,
local stability is the predicate

    Stable(A; N, E) iff E(A) <= E(B) for every B in N(A).

Minimality is evaluated relative to an explicitly supplied proper-subcandidate
family and an explicitly supplied neighborhood rule. These are executable
predicates over explicit inputs. They are not a claim that the preserved
historical theory has already proved a unique Unit-emergence theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Generic, Sequence, Tuple, TypeVar

T = TypeVar("T")
Energy = Callable[[T], float]
NeighborhoodRule = Callable[[T], "StabilityNeighborhood[T]"]


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
    neighborhood_rule: NeighborhoodRule[T],
    proper_subcandidates: Sequence[T],
    energy: Energy[T],
) -> bool:
    """Test stability plus absence of an explicitly supplied stable subcandidate.

    The caller supplies both the proper-subcandidate family and the
    neighborhood rule. This function does not infer containment, connectivity,
    or splitting from raw geometry.
    """
    if not is_locally_stable(candidate, neighborhood_rule(candidate), energy):
        return False

    return not any(
        is_locally_stable(subcandidate, neighborhood_rule(subcandidate), energy)
        for subcandidate in proper_subcandidates
    )


__all__ = [
    "StabilityNeighborhood",
    "is_locally_stable",
    "is_minimal_stable",
]
