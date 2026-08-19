"""Frozen Struct3D representation-space distance.

The frozen definition is

    D_R(W_1, W_2) = ||phi(W_1) - phi(W_2)||_2.

The representation object already fixes the 23-dimensional domain. This
module deliberately does not upgrade equality of representations into
structural identity: distinct worlds may have the same representation.
"""

from __future__ import annotations

import math

from .theory_representation import StructuralRepresentation


def structural_distance(a: StructuralRepresentation, b: StructuralRepresentation) -> float:
    """Return the Euclidean distance between two structural representations."""
    if len(a.values) != len(b.values):
        raise ValueError("representations must have equal dimension")

    squared = 0.0
    for x, y in zip(a.values, b.values):
        dx = float(x) - float(y)
        squared += dx * dx

    if not math.isfinite(squared):
        raise ValueError("representation coordinates must be finite")
    return math.sqrt(squared)
