"""Machine-readable boundary for the current Struct3D theory closure.

The current mathematical specification freezes W=(U,R,Phi) and the downstream
canonical/invariant/representation chain. Stage 2 separates upstream
formation contracts from conditional finite-set existence and uniqueness
results.

Status values are deliberately explicit:
    FROZEN_THEORY: directly represented by the specification.
    DERIVED: deterministic engineering construction from frozen objects.
    EXPLICIT_BOUNDARY: executable contract whose mathematical generator is not
        frozen by the preserved source.
    CONDITIONAL_THEOREM: proved under explicit hypotheses, without promoting
        those hypotheses into a universal observation-to-candidate theorem.
    THEORY_GAP: requires a future mathematical definition before promotion.
"""

from __future__ import annotations

from dataclasses import dataclass


FROZEN_THEORY = "FROZEN_THEORY"
DERIVED = "DERIVED"
EXPLICIT_BOUNDARY = "EXPLICIT_BOUNDARY"
CONDITIONAL_THEOREM = "CONDITIONAL_THEOREM"
THEORY_GAP = "THEORY_GAP"


@dataclass(frozen=True)
class Stage2Boundary:
    """Machine-readable status for a Stage-2 concept."""

    concept: str
    status: str
    mathematical_definition: str


STAGE2_CONTRACT = (
    Stage2Boundary("Observation", FROZEN_THEORY, "finite indexed universe X"),
    Stage2Boundary("CandidateFamily", EXPLICIT_BOUNDARY, "explicit finite A(X) input"),
    Stage2Boundary("Energy", EXPLICIT_BOUNDARY, "supplied finite scalar functional E"),
    Stage2Boundary("Stability", EXPLICIT_BOUNDARY, "Stable(A; N, E) over explicit N(A)"),
    Stage2Boundary("Minimality", EXPLICIT_BOUNDARY, "no explicitly supplied proper stable subcandidate"),
    Stage2Boundary(
        "Existence",
        CONDITIONAL_THEOREM,
        "non-empty finite A(X) + finite E => attained argmin",
    ),
    Stage2Boundary(
        "Uniqueness",
        CONDITIONAL_THEOREM,
        "strictly lower finite energy than every distinct competitor => unique argmin",
    ),
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
    "EXPLICIT_BOUNDARY",
    "CONDITIONAL_THEOREM",
    "THEORY_GAP",
    "Stage2Boundary",
    "STAGE2_CONTRACT",
    "stage2_status",
]
