"""Theory-facing partition selection for Struct3D.

The admissible candidate set and energy functional are explicit inputs.
No thresholding, connected-component rule, minimum-size filter, or additive
energy is introduced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Union

from .theory_core import Partition
from .theory_energy import EnergyResult, StructuralEnergy


@dataclass(frozen=True)
class PartitionSelection:
    partition: Partition
    energy: EnergyResult
    candidate_count: int


EnergyEvaluator = Union[Callable[[Partition], float], StructuralEnergy]


def select_minimum_energy_partition(
    candidates: Sequence[Partition],
    energy: EnergyEvaluator,
) -> PartitionSelection:
    """Select a minimum-energy partition from an explicit candidate set.

    Ties are resolved by the first candidate in the supplied ordered
    sequence. This is an implementation convention, not a claim that the
    mathematical minimizer is unique.
    """
    if not candidates:
        raise ValueError("At least one admissible partition is required")

    evaluator = energy if isinstance(energy, StructuralEnergy) else StructuralEnergy(energy)
    scored = [(candidate, evaluator(candidate)) for candidate in candidates]
    _, (best_partition, best_energy) = min(
        enumerate(scored), key=lambda item: item[1][1].value
    )
    return PartitionSelection(
        partition=best_partition,
        energy=best_energy,
        candidate_count=len(candidates),
    )


# Backward-compatible name retained for existing callers. It is intentionally
# an alias for energy minimization; perturbation stability is a separate
# predicate in theory_stability.py.
def select_stable_partition(
    candidates: Sequence[Partition],
    energy: EnergyEvaluator,
) -> PartitionSelection:
    return select_minimum_energy_partition(candidates, energy)
