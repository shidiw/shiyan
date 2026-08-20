"""Stage 2F: conditional existence of a global admissible minimizer.

The preserved Struct3D theory does not define the generator X -> A(X).  Stage
2F therefore proves only the strongest result justified by the current finite
core: if an explicit admissible family A(X) is non-empty and finite, and the
supplied energy is finite on that family, then an energy minimizer exists.

This is a finite-set existence theorem.  It is not a theorem that A(X) is
non-empty for every raw observation, and it is not a uniqueness theorem.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Tuple

from .theory_core import Partition


Energy = Callable[[Partition], float]


@dataclass(frozen=True)
class ExistenceResult:
    """Witness and value for the finite admissible minimization problem."""

    minimizer: Partition
    minimum_energy: float
    candidate_count: int


def prove_finite_minimizer_exists(
    candidates: Tuple[Partition, ...],
    energy: Energy,
) -> ExistenceResult:
    """Return an existing argmin under the Stage 2F hypotheses.

    Hypotheses enforced by the implementation:
      1. the admissible family is non-empty;
      2. every candidate is a valid finite Partition object;
      3. every supplied energy value is a finite real scalar.

    Under these conditions the candidate set is finite and non-empty, so the
    minimum of the finite set of energy values is attained by at least one
    candidate. Python's stable ``min`` supplies one witness on ties; no
    uniqueness is claimed.
    """
    if not candidates:
        raise ValueError("Stage 2F requires a non-empty admissible family")

    scored = []
    for candidate in candidates:
        value = float(energy(candidate))
        if not math.isfinite(value):
            raise ValueError("Stage 2F requires finite energy on every candidate")
        scored.append((candidate, value))

    minimizer, minimum_energy = min(scored, key=lambda item: item[1])
    return ExistenceResult(
        minimizer=minimizer,
        minimum_energy=minimum_energy,
        candidate_count=len(candidates),
    )


def has_materializable_witness(
    candidates: Tuple[Partition, ...],
    materializable: Callable[[Partition], bool],
) -> bool:
    """Check the explicit witness condition for a materializable candidate.

    This is deliberately a witness test, not an inferred existence theorem:
    the current theory does not prove that every observation has such a
    candidate.
    """
    if not candidates:
        return False
    return any(bool(materializable(candidate)) for candidate in candidates)


__all__ = [
    "ExistenceResult",
    "prove_finite_minimizer_exists",
    "has_materializable_witness",
]
