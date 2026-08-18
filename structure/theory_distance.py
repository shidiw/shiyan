"""Frozen Struct3D representation-space distance."""

from __future__ import annotations

import math

from .theory_representation import StructuralRepresentation


def structural_distance(a: StructuralRepresentation, b: StructuralRepresentation) -> float:
    """D_R(W1,W2) = ||phi(W1)-phi(W2)||_2."""
    if len(a.values) != len(b.values):
        raise ValueError("representations must have equal dimension")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a.values, b.values)))
