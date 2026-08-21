"""Stage 2E: theory-safe Structural Unit formation.

The frozen theory distinguishes three statements that must not be conflated:

1. a candidate unit is locally stable against an explicitly supplied
   perturbation neighborhood;
2. a candidate is minimal-stable relative to an explicitly supplied family of
   proper subcandidates; and
3. a stable candidate may be materialized as the single frozen StructuralUnit
   type.

Stage 2E may additionally verify an explicit positive energy margin against a
supplied competitor family. This is a verification of the Stage 2D separation
condition, not a new heuristic or a hidden source of competitors.

This module intentionally does not infer neighborhoods, merge rules,
thresholds, connectivity, primitive labels, or existence/uniqueness theorems
from raw geometry. Those are separate mathematical inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

from .theory_stability import StabilityNeighborhood, is_locally_stable, is_minimal_stable
from .theory_unit import StructuralUnit


Energy = Callable[[StructuralUnit], float]
NeighborhoodRule = Callable[[StructuralUnit], StabilityNeighborhood[StructuralUnit]]


def _validate_margin(margin: float) -> float:
    value = float(margin)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("energy margin must be finite and non-negative")
    return value


def has_energy_margin(
    unit: StructuralUnit,
    competitors: Sequence[StructuralUnit],
    energy: Energy,
    margin: float,
) -> bool:
    """Verify the one-sided positive margin required for Unit formation.

    For ``margin > 0`` the competitor family is mandatory and every distinct
    competitor must satisfy ``E(c) - E(unit) >= margin``. With ``margin=0``
    the margin contract is disabled, preserving the original Stage 2E API.
    """
    required_margin = _validate_margin(margin)
    if required_margin == 0.0:
        return True
    if not competitors:
        return False

    candidate_energy = float(energy(unit))
    if not math.isfinite(candidate_energy):
        raise ValueError("candidate energy must be finite")

    for competitor in competitors:
        competitor_energy = float(energy(competitor))
        if not math.isfinite(competitor_energy):
            raise ValueError("competitor energy must be finite")
        if competitor != unit and competitor_energy - candidate_energy < required_margin:
            return False
    return True


@dataclass(frozen=True)
class UnitFormationResult:
    """Executable result of an explicitly specified Unit-formation predicate."""

    unit: StructuralUnit
    stable: bool
    minimal_stable: bool
    margin_separated: bool = True

    @property
    def materializable(self) -> bool:
        """Whether the supplied predicates permit materializing this Unit."""
        return self.stable and self.minimal_stable and self.margin_separated


def evaluate_unit_formation(
    unit: StructuralUnit,
    neighborhood_rule: NeighborhoodRule,
    proper_subcandidates: Sequence[StructuralUnit],
    energy: Energy,
    energy_margin: float = 0.0,
    margin_competitors: Sequence[StructuralUnit] = (),
) -> UnitFormationResult:
    """Evaluate Stage 2E predicates for one explicit candidate Unit.

    ``proper_subcandidates``, ``neighborhood_rule`` and, when requested,
    ``margin_competitors`` are mandatory theory inputs. No geometric heuristic
    is introduced by this function.
    """
    neighborhood = neighborhood_rule(unit)
    stable = is_locally_stable(unit, neighborhood, energy)
    minimal_stable = is_minimal_stable(
        unit,
        neighborhood_rule,
        tuple(proper_subcandidates),
        energy,
    )
    margin_separated = has_energy_margin(
        unit,
        tuple(margin_competitors),
        energy,
        energy_margin,
    )
    return UnitFormationResult(
        unit=unit,
        stable=stable,
        minimal_stable=minimal_stable,
        margin_separated=margin_separated,
    )


def materialize_unit(
    unit: StructuralUnit,
    neighborhood_rule: NeighborhoodRule,
    proper_subcandidates: Sequence[StructuralUnit],
    energy: Energy,
    energy_margin: float = 0.0,
    margin_competitors: Sequence[StructuralUnit] = (),
) -> StructuralUnit:
    """Materialize a candidate iff all supplied Stage 2E predicates pass."""
    result = evaluate_unit_formation(
        unit,
        neighborhood_rule,
        proper_subcandidates,
        energy,
        energy_margin,
        margin_competitors,
    )
    if not result.materializable:
        raise ValueError("candidate does not satisfy the supplied Stage 2E Unit predicates")
    return result.unit


__all__ = [
    "UnitFormationResult",
    "evaluate_unit_formation",
    "has_energy_margin",
    "materialize_unit",
]
