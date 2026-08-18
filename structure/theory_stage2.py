"""Stage-2 boundary for structures not formally defined by the frozen theory.

The current mathematical specification freezes W=(U,R,Phi).  It does not
formally define Object, Instance, or Hierarchy emergence.  This module makes
that boundary executable instead of silently extending the theory.

Status values are deliberately explicit:
    FROZEN_THEORY: directly represented by the specification.
    DERIVED: deterministic engineering construction from frozen objects.
    THEORY_GAP: requires a future mathematical definition before promotion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


FROZEN_THEORY = "FROZEN_THEORY"
DERIVED = "DERIVED"
THEORY_GAP = "THEORY_GAP"


@dataclass(frozen=True)
class Stage2Boundary:
    """Machine-readable status for a Stage-2 concept."""

    concept: str
    status: str
    mathematical_definition: str


STAGE2_CONTRACT = (
    Stage2Boundary("Unit", FROZEN_THEORY, "u=(G,theta)"),
    Stage2Boundary("Relation", FROZEN_THEORY, "r_ij between Units"),
    Stage2Boundary("Graph", FROZEN_THEORY, "G=(V,E)"),
    Stage2Boundary("World", FROZEN_THEORY, "W=(U,R,Phi)"),
    Stage2Boundary("Object", DERIVED, "explicit assembly-connected Units"),
    Stage2Boundary("Instance", THEORY_GAP, "not formally defined in frozen specification"),
    Stage2Boundary("Hierarchy", THEORY_GAP, "not formally defined in frozen specification"),
)


def stage2_status(concept: str) -> Stage2Boundary:
    for item in STAGE2_CONTRACT:
        if item.concept == concept:
            return item
    raise KeyError(concept)


__all__ = [
    "FROZEN_THEORY",
    "DERIVED",
    "THEORY_GAP",
    "Stage2Boundary",
    "STAGE2_CONTRACT",
    "stage2_status",
]
