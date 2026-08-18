"""Theory-aligned neural objectives for Neural Struct3D.

This module keeps the v1.0 reconstruction objective separate from the
later distance-preserving objective. It does not prescribe network
architecture or hyperparameters.
"""

from __future__ import annotations

import math
from typing import Sequence


def reconstruction_loss(target: Sequence[float], reconstruction: Sequence[float]) -> float:
    if len(target) != len(reconstruction):
        raise ValueError("target and reconstruction must have equal dimension")
    return sum((float(a) - float(b)) ** 2 for a, b in zip(target, reconstruction))


def distance_preservation_loss(latent_a: Sequence[float], latent_b: Sequence[float], structural_distance: float, eps: float = 1e-12) -> float:
    """Squared relative distance mismatch used by the distance-preserving direction."""
    latent_distance = math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(latent_a, latent_b)))
    target = float(structural_distance)
    return ((latent_distance - target) / (target + eps)) ** 2


def mutation_consistency_loss(latent_distance: float, structural_distance: float, eps: float = 1e-12) -> float:
    """Penalize latent collapse when a representation-level mutation is nonzero."""
    if structural_distance <= 0:
        return 0.0
    if latent_distance > 0:
        return 0.0
    return 1.0


def combined_loss(
    recon: float,
    distance: float,
    mutation: float,
    lambda_distance: float,
    lambda_mutation: float,
) -> float:
    if lambda_distance < 0 or lambda_mutation < 0:
        raise ValueError("loss weights must be non-negative")
    return float(recon) + lambda_distance * float(distance) + lambda_mutation * float(mutation)
