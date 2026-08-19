"""Theory-aligned neural objectives for Neural Struct3D.

The frozen structural distance lives in representation space. Neural losses
are optimization objectives only; they do not redefine structural identity
and do not claim exact metric preservation unless an independently verified
model satisfies such a property.
"""

from __future__ import annotations

import math
from typing import Sequence


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def reconstruction_loss(target: Sequence[float], reconstruction: Sequence[float]) -> float:
    if len(target) != len(reconstruction):
        raise ValueError("target and reconstruction must have equal dimension")
    total = 0.0
    for a, b in zip(target, reconstruction):
        diff = _finite(a, "target coordinate") - _finite(b, "reconstruction coordinate")
        total += diff * diff
    return total


def distance_preservation_loss(
    latent_a: Sequence[float],
    latent_b: Sequence[float],
    structural_distance: float,
    eps: float = 1e-12,
) -> float:
    """Squared relative mismatch between latent and structural distances."""
    if len(latent_a) != len(latent_b):
        raise ValueError("latent representations must have equal dimension")
    target = _finite(structural_distance, "structural_distance")
    if target < 0:
        raise ValueError("structural_distance must be non-negative")
    eps = _finite(eps, "eps")
    if eps <= 0:
        raise ValueError("eps must be positive")

    squared = 0.0
    for a, b in zip(latent_a, latent_b):
        diff = _finite(a, "latent coordinate") - _finite(b, "latent coordinate")
        squared += diff * diff
    latent_distance = math.sqrt(squared)
    return ((latent_distance - target) / (target + eps)) ** 2


def mutation_consistency_loss(latent_distance: float, structural_distance: float, eps: float = 1e-12) -> float:
    """Penalize latent collapse when a representation-level mutation is nonzero."""
    latent_distance = _finite(latent_distance, "latent_distance")
    structural_distance = _finite(structural_distance, "structural_distance")
    eps = _finite(eps, "eps")
    if latent_distance < 0 or structural_distance < 0:
        raise ValueError("distances must be non-negative")
    if eps <= 0:
        raise ValueError("eps must be positive")
    if structural_distance <= eps:
        return 0.0
    return 0.0 if latent_distance > eps else 1.0


def combined_loss(
    recon: float,
    distance: float,
    mutation: float,
    lambda_distance: float,
    lambda_mutation: float,
) -> float:
    recon = _finite(recon, "reconstruction loss")
    distance = _finite(distance, "distance loss")
    mutation = _finite(mutation, "mutation loss")
    lambda_distance = _finite(lambda_distance, "lambda_distance")
    lambda_mutation = _finite(lambda_mutation, "lambda_mutation")
    if min(recon, distance, mutation) < 0:
        raise ValueError("loss terms must be non-negative")
    if lambda_distance < 0 or lambda_mutation < 0:
        raise ValueError("loss weights must be non-negative")
    return recon + lambda_distance * distance + lambda_mutation * mutation
