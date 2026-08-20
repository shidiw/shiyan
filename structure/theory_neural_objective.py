"""Theory-facing neural objective contract.

The frozen structural theory defines representation-space distance, but does
not by itself prove that a neural latent space preserves that distance. This
module therefore exposes the objective as an explicit contract rather than a
theorem.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class NeuralObjective:
    """Explicit coefficients for candidate neural training objectives."""

    reconstruction_weight: float = 1.0
    distance_weight: float = 0.0
    mutation_weight: float = 0.0

    def __post_init__(self) -> None:
        for value in (
            self.reconstruction_weight,
            self.distance_weight,
            self.mutation_weight,
        ):
            if not math.isfinite(float(value)) or value < 0.0:
                raise ValueError("objective weights must be finite and non-negative")


def combine_losses(
    reconstruction: float,
    distance: float,
    mutation: float,
    objective: NeuralObjective,
) -> float:
    """Combine explicitly supplied loss terms; no neural claim is implied."""
    terms = (reconstruction, distance, mutation)
    if not all(math.isfinite(float(value)) for value in terms):
        raise ValueError("loss terms must be finite real scalars")
    return (
        objective.reconstruction_weight * reconstruction
        + objective.distance_weight * distance
        + objective.mutation_weight * mutation
    )


__all__ = ["NeuralObjective", "combine_losses"]
