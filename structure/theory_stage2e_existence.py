"""Observation-derived Stage 2E existence theorem for Struct3D.

For a valid finite observation X, the canonical Unit candidate family is the
set of all non-empty observation supports because Gamma(X)=A_max(X)=Pi(Omega_X).
The Stage 2D unit energy is finite on this family. A finite non-empty family
therefore has a global unit-energy minimizer. Because the frozen N_X
insertion/deletion neighborhood stays inside the same family, a global
minimizer is stable. The finite stable subset has a minimum-support element,
which is MinimalStable under the existing S_X contract.

A strict positive Stage 2E margin is handled separately and correctly: it is
available only when an observation-derived Unit is simultaneously
Stable, MinimalStable, and strictly lower in Stage 2D unit energy than every
other X-derived Unit. No external margin is supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Optional, Sequence, Tuple

from .theory_core import StructuralUnit
from .theory_unit_formation import evaluate_observation_unit_formation
from .theory_stability import is_locally_stable

Energy = Callable[[StructuralUnit], float]


@dataclass(frozen=True)
class Stage2EExistenceResult:
    """Canonical witness and derived margin for observation-derived Stage 2E."""

    unit: StructuralUnit
    stable_unit_count: int
    candidate_count: int
    derived_unit_margin: float
    strict_margin_available: bool

    @property
    def materializable(self) -> bool:
        return True


def _finite_unit_energy(unit: StructuralUnit, energy: Energy) -> float:
    value = float(energy(unit))
    if not math.isfinite(value):
        raise ValueError("Stage 2E requires finite unit energy on every candidate")
    return value


def _support_key(unit: StructuralUnit) -> Tuple[int, ...]:
    return tuple(unit.indices)


def observation_unit_family_is_complete(context) -> bool:
    """Verify that the X-derived Unit family contains every non-empty support."""
    n = len(context.observation.points)
    expected = {
        tuple(i for i in range(n) if mask & (1 << i))
        for mask in range(1, 1 << n)
    }
    actual = {_support_key(unit) for unit in context.unit_candidates}
    return actual == expected


def derived_unit_energy_margin(
    candidates: Sequence[StructuralUnit],
    energy: Energy,
) -> float:
    """Return the global pairwise Unit-energy separation Delta_U(X).

    The value is zero whenever two distinct Units are energy-tied. Therefore
    Delta_U(X)>0 is exactly strict pairwise separation of all X-derived Units.
    This quantity alone does not assert Stage 2E MinimalStable compatibility.
    """
    if not candidates:
        raise ValueError("Stage 2E requires a non-empty Unit candidate family")
    values = [_finite_unit_energy(unit, energy) for unit in candidates]
    if len(values) == 1:
        return 0.0
    minimum = math.inf
    for i, first in enumerate(values):
        for second in values[i + 1 :]:
            minimum = min(minimum, abs(first - second))
    return float(minimum)


def _is_minimal_stable(unit: StructuralUnit, context, energy: Energy) -> bool:
    result = evaluate_observation_unit_formation(
        unit,
        context,
        energy,
        energy_margin=0.0,
    )
    return result.materializable


def _strict_witness_margin(
    unit: StructuralUnit,
    candidates: Sequence[StructuralUnit],
    energy: Energy,
) -> float:
    """Return the directional global margin required by Stage 2E.

    A positive value means this Unit is strictly lower-energy than every other
    X-derived Unit. A non-positive value means it cannot satisfy a positive
    margin against the complete observation-derived competitor family.
    """
    candidate_energy = _finite_unit_energy(unit, energy)
    gaps = [
        _finite_unit_energy(other, energy) - candidate_energy
        for other in candidates
        if other != unit
    ]
    if not gaps:
        return 0.0
    margin = min(gaps)
    return margin if margin > 0.0 else 0.0


def prove_observation_derived_stage2e_existence(
    context,
    energy: Optional[Energy] = None,
    *,
    require_strict_margin: bool = False,
) -> Stage2EExistenceResult:
    """Prove and return an observation-derived Stage 2E Unit witness.

    Proof structure:
      1. X is finite and non-empty, so the canonical Unit family is finite and
         non-empty.
      2. Gamma(X)=A_max(X) contains every non-empty support; every N_X
         insertion/deletion alternative therefore belongs to the same family.
      3. Finite unit-energy values attain a global minimum at some v.
      4. v is locally stable because no candidate, hence no N_X alternative,
         has lower unit energy.
      5. The stable subset is finite and non-empty. Choosing a stable unit of
         minimum support cardinality makes it MinimalStable under the frozen
         S_X family, whose members have strictly smaller support cardinality.
      6. With the canonical zero-margin contract, this proves Unit existence.
         For a positive margin, the theorem searches the same X-derived finite
         family for a Unit that is both Stable/MinimalStable and has a positive
         directional gap against every other Unit.
    """
    candidates = tuple(context.unit_candidates)
    if not candidates:
        raise ValueError("Observation-derived Stage 2E candidate family is empty")
    if not observation_unit_family_is_complete(context):
        raise ValueError("Canonical Unit candidate family is not the complete non-empty support family")

    stage2d = context.stage2d_energy() if energy is None else None
    unit_energy: Energy = stage2d.unit_energy if stage2d is not None else energy  # type: ignore[assignment]
    if unit_energy is None:
        raise ValueError("An observation-derived Stage 2D unit energy is required")

    scored = tuple((unit, _finite_unit_energy(unit, unit_energy)) for unit in candidates)
    global_min = min(value for _, value in scored)

    stable_units = []
    for unit, _ in scored:
        if is_locally_stable(unit, context.neighborhood_rule(unit), unit_energy):
            stable_units.append(unit)

    if not stable_units:
        raise AssertionError("Finite global minimization must produce at least one stable Unit")

    minimal_stable_units = [
        unit for unit in stable_units if _is_minimal_stable(unit, context, unit_energy)
    ]
    if not minimal_stable_units:
        raise AssertionError("Finite stable-set minimality must produce a Stage 2E witness")

    # Canonical zero-margin witness: minimum support, then lexicographic support.
    selected = min(
        minimal_stable_units,
        key=lambda u: (len(u.indices), _support_key(u)),
    )

    strict_candidates = []
    for unit in minimal_stable_units:
        margin = _strict_witness_margin(unit, candidates, unit_energy)
        if margin > 0.0:
            strict_candidates.append((unit, margin))

    if require_strict_margin:
        if not strict_candidates:
            raise ValueError(
                "No observation-derived Stage 2E Unit has a positive global energy margin"
            )
        # Unique global minimum under positive margin; deterministic fallback
        # ordering remains explicit for complete reproducibility.
        selected, selected_margin = min(
            strict_candidates,
            key=lambda item: (-item[1], len(item[0].indices), _support_key(item[0])),
        )
    else:
        selected_margin = _strict_witness_margin(selected, candidates, unit_energy)

    formation = evaluate_observation_unit_formation(
        selected,
        context,
        unit_energy,
        energy_margin=selected_margin if require_strict_margin else 0.0,
    )
    if not formation.materializable:
        raise AssertionError("Selected observation-derived Stage 2E witness violates its own contract")

    pairwise_margin = derived_unit_energy_margin(candidates, unit_energy)
    if not math.isfinite(global_min):
        raise AssertionError("Finite candidate energies must attain a finite minimum")

    return Stage2EExistenceResult(
        unit=selected,
        stable_unit_count=len(stable_units),
        candidate_count=len(candidates),
        derived_unit_margin=(selected_margin if require_strict_margin else pairwise_margin),
        strict_margin_available=bool(strict_candidates),
    )


__all__ = [
    "Stage2EExistenceResult",
    "observation_unit_family_is_complete",
    "derived_unit_energy_margin",
    "prove_observation_derived_stage2e_existence",
]
