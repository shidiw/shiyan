"""Stage 2H: canonical finite candidate space and Unit emergence.

This module closes the previously open upstream boundary without introducing a
geometric threshold or a hidden discovery heuristic.

For a finite non-empty observation domain X, the canonical candidate family is
all non-empty finite supports S subseteq X, represented as the frozen
StructuralUnit(S, {}). The attribute field is intentionally empty at emergence:
attribute enrichment is downstream metadata and is not needed to define support
admissibility.

A candidate competes against every other candidate in A(X). Thus local
stability is instantiated as global minimality over the finite candidate family.
Stage 2E minimal-stability then selects inclusion-minimal global minimizers.
This is an existence theorem, not a uniqueness claim.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Tuple

from .theory_stability import StabilityNeighborhood
from .theory_unit import StructuralUnit


Energy = Callable[[StructuralUnit], float]


@dataclass(frozen=True)
class ObservationDomain:
    """Finite non-empty indexed observation domain X."""

    indices: Tuple[int, ...]

    def __post_init__(self) -> None:
        normalized = tuple(sorted(int(i) for i in self.indices))
        if not normalized:
            raise ValueError("Observation domain must be non-empty")
        if any(i < 0 for i in normalized):
            raise ValueError("Observation indices must be nonnegative")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Observation indices must be unique")
        object.__setattr__(self, "indices", normalized)


def admissible_candidates(domain: ObservationDomain) -> Tuple[StructuralUnit, ...]:
    """Return the canonical finite family A(X) of all non-empty supports."""
    values = domain.indices
    candidates = []
    for size in range(1, len(values) + 1):
        for support in combinations(values, size):
            candidates.append(StructuralUnit(support, {}))
    return tuple(candidates)


def candidate_neighborhood(
    candidate: StructuralUnit,
    family: Tuple[StructuralUnit, ...],
) -> StabilityNeighborhood[StructuralUnit]:
    """Instantiate Stage 2E stability against every competing candidate."""
    alternatives = tuple(other for other in family if other != candidate)
    if not alternatives:
        # The historical executable neighborhood requires one alternative;
        # self is a neutral equality witness for the one-element family.
        alternatives = (candidate,)
    return StabilityNeighborhood(alternatives)


def stable_candidates(
    domain: ObservationDomain,
    energy: Energy,
) -> Tuple[StructuralUnit, ...]:
    """Return all global minimizers of E over A(X)."""
    family = admissible_candidates(domain)
    values = tuple(float(energy(candidate)) for candidate in family)
    if any(not math.isfinite(value) for value in values):
        raise ValueError("Unit emergence energy must be finite on every candidate")
    minimum = min(values)
    return tuple(candidate for candidate, value in zip(family, values) if value == minimum)


def emergent_units(
    domain: ObservationDomain,
    energy: Energy,
) -> Tuple[StructuralUnit, ...]:
    """Return inclusion-minimal stable candidates.

    Because A(X) is finite and non-empty, at least one global minimizer exists.
    If a global minimizer has a proper stable subcandidate, descend to that
    subcandidate. Finiteness guarantees termination at an inclusion-minimal
    stable candidate. Hence the returned set is non-empty.
    """
    stable = stable_candidates(domain, energy)
    stable_supports = {unit.indices for unit in stable}

    result = []
    for candidate in stable:
        candidate_support = set(candidate.indices)
        has_stable_proper_subset = any(
            set(support) < candidate_support
            for support in stable_supports
        )
        if not has_stable_proper_subset:
            result.append(candidate)
    if not result:
        raise AssertionError("finite stable candidate family must contain an inclusion-minimal element")
    return tuple(result)


def materialize_emergent_unit(
    domain: ObservationDomain,
    energy: Energy,
) -> StructuralUnit:
    """Materialize one emergent Unit without claiming uniqueness.

    Ties are resolved deterministically by canonical support order only as an
    engineering selection rule. The mathematical result remains set-valued
    whenever multiple inclusion-minimal minimizers exist.
    """
    units = emergent_units(domain, energy)
    return min(units, key=lambda unit: (len(unit.indices), unit.indices))


__all__ = [
    "ObservationDomain",
    "admissible_candidates",
    "candidate_neighborhood",
    "stable_candidates",
    "emergent_units",
    "materialize_emergent_unit",
]
