"""Stage 2G: conditional uniqueness of an admissible minimizer.

The finite existence theorem guarantees an attained minimum, but not a unique
one. Stage 2G makes the missing uniqueness hypothesis explicit: a minimizer is
unique exactly when its energy is strictly smaller than every distinct
admissible competitor.

A positive ``margin`` strengthens strict separation to the theorem-level
condition

    E(C) - E(A) >= margin > 0

for every distinct competitor C of candidate A. The margin is supplied and
verified; it is never manufactured by deterministic tie-breaking.
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
    margin: float = 0.0


def _validate_margin(margin: float) -> float:
    value = float(margin)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("uniqueness margin must be finite and non-negative")
    return value


def is_unique_minimizer(
    candidate: Partition,
    competitors: Tuple[Partition, ...],
    energy: Energy,
    margin: float = 0.0,
) -> bool:
    """Return whether ``candidate`` is a strict minimizer over competitors.

    With ``margin=0`` this preserves the original Stage 2G strict-minimum
    contract. With ``margin>0`` every distinct competitor must exceed the
    candidate by at least that margin. Equal-energy ties therefore return
    ``False`` and a positive-margin claim cannot be inferred from ordering.
    """
    required_margin = _validate_margin(margin)
    candidate_energy = float(energy(candidate))
    if not math.isfinite(candidate_energy):
        raise ValueError("candidate energy must be finite")

    for competitor in competitors:
        competitor_energy = float(energy(competitor))
        if not math.isfinite(competitor_energy):
            raise ValueError("competitor energy must be finite")
        if competitor != candidate and competitor_energy - candidate_energy < required_margin:
            return False
    return True


def prove_unique_minimizer(
    candidate: Partition,
    competitors: Tuple[Partition, ...],
    energy: Energy,
    margin: float = 0.0,
) -> UniquenessResult:
    """Return a uniqueness witness when the requested separation succeeds."""
    required_margin = _validate_margin(margin)
    value = float(energy(candidate))
    if not math.isfinite(value):
        raise ValueError("candidate energy must be finite")
    unique = is_unique_minimizer(candidate, competitors, energy, required_margin)
    if not unique:
        raise ValueError("candidate is not a uniquely minimizing admissible partition")
    return UniquenessResult(
        candidate=candidate,
        energy=value,
        unique=True,
        margin=required_margin,
    )


__all__ = ["UniquenessResult", "is_unique_minimizer", "prove_unique_minimizer"]
