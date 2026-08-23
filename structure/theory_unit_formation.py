"""Stage 2E: theory-safe Structural Unit formation.

The low-level API still accepts explicit predicates for regression compatibility.
The observation-derived API removes that external boundary by obtaining
N_X, S_X, and the Unit competitor family directly from one observation-derived
context.
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
    unit: StructuralUnit
    stable: bool
    minimal_stable: bool
    margin_separated: bool = True

    @property
    def materializable(self) -> bool:
        return self.stable and self.minimal_stable and self.margin_separated


def evaluate_unit_formation(
    unit: StructuralUnit,
    neighborhood_rule: NeighborhoodRule,
    proper_subcandidates: Sequence[StructuralUnit],
    energy: Energy,
    energy_margin: float = 0.0,
    margin_competitors: Sequence[StructuralUnit] = (),
) -> UnitFormationResult:
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
    return UnitFormationResult(unit, stable, minimal_stable, margin_separated)


def evaluate_observation_unit_formation(
    unit: StructuralUnit,
    context,
    energy: Energy,
    energy_margin: float = 0.0,
) -> UnitFormationResult:
    """Evaluate Stage 2E with N_X, S_X and competitors derived from X."""
    return evaluate_unit_formation(
        unit=unit,
        neighborhood_rule=context.neighborhood_rule,
        proper_subcandidates=context.proper_subcandidates(unit),
        energy=energy,
        energy_margin=energy_margin,
        margin_competitors=context.unit_candidates,
    )


def materialize_unit(
    unit: StructuralUnit,
    neighborhood_rule: NeighborhoodRule,
    proper_subcandidates: Sequence[StructuralUnit],
    energy: Energy,
    energy_margin: float = 0.0,
    margin_competitors: Sequence[StructuralUnit] = (),
) -> StructuralUnit:
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


def materialize_observation_unit(
    unit: StructuralUnit,
    context,
    energy: Energy,
    energy_margin: float = 0.0,
) -> StructuralUnit:
    """Materialize a Unit using only observation-derived Stage 2E boundaries."""
    result = evaluate_observation_unit_formation(unit, context, energy, energy_margin)
    if not result.materializable:
        raise ValueError("candidate does not satisfy observation-derived Stage 2E predicates")
    return result.unit


__all__ = [
    "UnitFormationResult",
    "evaluate_unit_formation",
    "evaluate_observation_unit_formation",
    "has_energy_margin",
    "materialize_unit",
    "materialize_observation_unit",
]
