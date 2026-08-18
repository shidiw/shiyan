"""Theory-facing energy interface for Struct3D.

This module intentionally does NOT invent an additive decomposition.
The formal theory must supply a scalar functional E on admissible candidates.
Legacy energy remains in ``structure.energy`` for regression comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from .theory_core import Partition, TheoryUnit

T = TypeVar("T")


@dataclass(frozen=True)
class EnergyResult:
    """A scalar energy value with explicit provenance."""

    value: float
    source: str = "theory"

    def __post_init__(self) -> None:
        if self.value != self.value:
            raise ValueError("Energy cannot be NaN")


class StructuralEnergy:
    """Evaluate an explicitly supplied Struct3D energy functional.

    No default weights, regularizers, thresholds, or primitive dimensions are
    introduced here. This keeps the theory layer faithful until the formal
    energy definition is fixed.
    """

    def __init__(self, functional: Callable[[Partition], float]):
        self.functional = functional

    def __call__(self, partition: Partition) -> EnergyResult:
        return EnergyResult(float(self.functional(partition)))


def candidate_energy(
    unit: TheoryUnit,
    functional: Callable[[TheoryUnit], float],
) -> EnergyResult:
    """Evaluate a unit-level functional supplied by the formal theory."""
    return EnergyResult(float(functional(unit)))
