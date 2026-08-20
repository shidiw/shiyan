"""Stage 2E: theory-safe Structural Unit formation.

The frozen theory distinguishes three statements that must not be conflated:

1. a candidate unit is locally stable against an explicitly supplied
   perturbation neighborhood;
2. a candidate is minimal-stable relative to an explicitly supplied family of
   proper subcandidates; and
3. a stable candidate may be materialized as the single frozen StructuralUnit
   type.

This module intentionally does not infer neighborhoods, merge rules,
thresholds, connectivity, primitive labels, or existence/uniqueness theorems
from raw geometry. Those are separate mathematical inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence, Tuple

from .theory_stability import StabilityNeighborhood, is_locally_stable, is_minimal_stable
from .theory_unit import StructuralUnit


Energy = Callable[[StructuralUnit], float]
NeighborhoodRule = Callable[[StructuralUnit], StabilityNeighborhood[StructuralUnit]]


@dataclass(frozen=True)
class UnitFormationResult:
    """Executable result of an explicitly specified Unit-formation predicate."""

    unit: StructuralUnit
    stable: bool
    minimal_stable: bool

    @property
    def materializable(self) -> bool:
        """Whether the supplied predicates permit materializing this Unit."""
        return self.stable and self.minimal_stable


def evaluate_unit_formation(
    unit: StructuralUnit,
    neighborhood_rule: NeighborhoodRule,
    proper_subcandidates: Sequence[StructuralUnit],
    energy: Energy,
) -> UnitFormationResult:
    """Evaluate Stage 2E predicates for one explicit candidate Unit.

    ``proper_subcandidates`` and ``neighborhood_rule`` are mandatory theory
    inputs. No geometric heuristic is introduced by this function.
    """
    neighborhood = neighborhood_rule(unit)
    stable = is_locally_stable(unit, neighborhood, energy)
    minimal_stable = is_minimal_stable(
        unit,
        neighborhood_rule,
        tuple(proper_subcandidates),
        energy,
    )
    return UnitFormationResult(
        unit=unit,
        stable=stable,
        minimal_stable=minimal_stable,
    )


def materialize_unit(
    unit: StructuralUnit,
    neighborhood_rule: NeighborhoodRule,
    proper_subcandidates: Sequence[StructuralUnit],
    energy: Energy,
) -> StructuralUnit:
    """Materialize a candidate as a frozen StructuralUnit iff Stage 2E passes.

    Failure is explicit: this function never silently converts an unstable or
    non-minimal candidate into a Unit.
    """
    result = evaluate_unit_formation(
        unit,
        neighborhood_rule,
        proper_subcandidates,
        energy,
    )
    if not result.materializable:
        raise ValueError("candidate does not satisfy the supplied Stage 2E Unit predicates")
    return result.unit


__all__ = [
    "UnitFormationResult",
    "evaluate_unit_formation",
    "materialize_unit",
]
