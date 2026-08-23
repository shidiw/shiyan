"""Observation-derived Stage 2E existence theorem for Struct3D.

For a valid finite observation X, the canonical Unit candidate family is the
set of all non-empty observation supports because Gamma(X)=A_max(X)=Pi(Omega_X).
The Stage 2D unit energy is finite on this family. A finite non-empty family
therefore has a global unit-energy minimizer. Because the frozen N_X
insertion/deletion neighborhood stays inside the same family, a global
minimizer is stable. The finite stable subset has a minimum-support element,
which is MinimalStable under the existing S_X contract.

A strict positive Stage 2E margin is a separate, observation-derived property:
Delta_U(X) is the minimum pairwise unit-energy gap, with any energy tie forcing
Delta_U(X)=0. It is not assumed or supplied by a caller.
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
    """Return Delta_U(X), the minimum pairwise unit-energy gap.

    The value is zero whenever two distinct candidates are energy-tied. Hence
    Delta_U(X)>0 is exactly the strict pairwise separation condition required
    for a positive Unit margin. The quantity is a deterministic statistic of X
    through its canonical candidate family and Stage 2D unit energy.
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
      3. Finite unit-energy values attain a global minimum at some u*.
      4. u* is locally stable because no candidate, hence no N_X alternative,
         has lower unit energy.
      5. The stable subset is finite and non-empty. Choosing a stable unit of
         minimum support cardinality makes it MinimalStable under the frozen
         S_X family, whose members have strictly smaller support cardinality.
      6. With the default zero-margin Stage 2E contract, this witness is
         materializable. Strict-margin materialization additionally requires
         the derived Delta_U(X)>0; no external margin is accepted.
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

    # Finite global minimization proves that the stable subset is non-empty.
    scored = tuple((unit, _finite_unit_energy(unit, unit_energy)) for unit in candidates)
    global_min = min(value for _, value in scored)

    stable_units = []
    for unit, value in scored:
        neighborhood = context.neighborhood_rule(unit)
        if is_locally_stable(unit, neighborhood, unit_energy):
            stable_units.append(unit)

    if not stable_units:
        raise AssertionError("Finite global minimization must produce at least one stable Unit")

    # Among the finite stable set, choose minimum support cardinality. Every
    # member of the frozen S_X(candidate) family has strictly smaller support,
    # so no such member can itself be stable. This is exactly the current
    # MinimalStable contract, without introducing a new semantic predicate.
    selected = min(stable_units, key=lambda u: (len(u.indices), _support_key(u)))
    formation = evaluate_observation_unit_formation(
        selected,
        context,
        unit_energy,
        energy_margin=0.0,
    )
    if not formation.materializable:
        raise AssertionError("Minimum-support stable Unit must satisfy the Stage 2E contract")

    margin = derived_unit_energy_margin(candidates, unit_energy)
    strict_available = margin > 0.0
    if require_strict_margin and not strict_available:
        raise ValueError(
            "Strict Stage 2E margin is not observation-guaranteed: "
            f"derived Delta_U={margin}"
        )

    if not math.isfinite(global_min):
        raise AssertionError("Finite candidate energies must attain a finite minimum")

    return Stage2EExistenceResult(
        unit=selected,
        stable_unit_count=len(stable_units),
        candidate_count=len(candidates),
        derived_unit_margin=margin,
        strict_margin_available=strict_available,
    )


__all__ = [
    "Stage2EExistenceResult",
    "observation_unit_family_is_complete",
    "derived_unit_energy_margin",
    "prove_observation_derived_stage2e_existence",
]
