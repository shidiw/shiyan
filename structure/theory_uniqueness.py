"""Stage 2G: conditional uniqueness of an admissible minimizer.

The finite existence theorem guarantees an attained minimum, but not a unique
one. Stage 2G makes the missing uniqueness hypothesis explicit: a minimizer is
unique exactly when its energy is strictly smaller than every distinct
admissible competitor.

This module deliberately does not identify tied candidates by a deterministic
Python ordering, and it does not claim structural equivalence from equal
energy or equal representation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Tuple

from .theory_core import Partition


Energy = Callable[[Partition], float]


@dataclass(frozen=True)
class UniquenessResult:
    """Conditional uniqueness result for one explicit candidate."""

    candidate: Partition
    energy: float
    unique: bool


def is_unique_minimizer(
    candidate: Partition,
    competitors: Tuple[Partition, ...],
    energy: Energy,
) -> bool:
    """Return whether ``candidate`` is a strict minimizer over competitors.

    The supplied competitors are the complete comparison family for this
    call. Distinct candidates must have strictly greater energy. Equal-energy
    ties therefore return ``False`` rather than being resolved by ordering.
    """
    candidate_energy = float(energy(candidate))
    if not math.isfinite(candidate_energy):
        raise ValueError("candidate energy must be finite")

    for competitor in competitors:
        competitor_energy = float(energy(competitor))
        if not math.isfinite(competitor_energy):
            raise ValueError("competitor energy must be finite")
        if competitor != candidate and competitor_energy <= candidate_energy:
            return False
    return True


def prove_unique_minimizer(
    candidate: Partition,
    competitors: Tuple[Partition, ...],
    energy: Energy,
) -> UniquenessResult:
    """Return a uniqueness witness when strict comparison succeeds."""
    value = float(energy(candidate))
    if not math.isfinite(value):
        raise ValueError("candidate energy must be finite")
    unique = is_unique_minimizer(candidate, competitors, energy)
    if not unique:
        raise ValueError("candidate is not a uniquely minimizing admissible partition")
    return UniquenessResult(candidate=candidate, energy=value, unique=True)


__all__ = ["UniquenessResult", "is_unique_minimizer", "prove_unique_minimizer"]
