"""The frozen v4.0 representation schema.

The theory fixes only the 23-dimensional grouping, not a unique numerical
estimator for every statistic. Therefore this module freezes the coordinate
contract without inventing feature formulas.

phi(W) = [h_P, h_O, t_O, h_R, s_R, o_I, g] in R^23
with group sizes 3,3,3,3,3,3,5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


REPRESENTATION_GROUPS: Tuple[Tuple[str, int], ...] = (
    ("primitive_histogram", 3),
    ("object_composition_histogram", 3),
    ("object_count_topology", 3),
    ("relation_type_histogram", 3),
    ("relation_confidence_statistics", 3),
    ("instance_occupancy_statistics", 3),
    ("global_structural_counts", 5),
)

REPRESENTATION_DIM = sum(size for _, size in REPRESENTATION_GROUPS)


def group_slices():
    """Return the frozen half-open coordinate ranges for the seven groups."""
    result = {}
    start = 0
    for name, size in REPRESENTATION_GROUPS:
        result[name] = slice(start, start + size)
        start += size
    return result


def validate_grouped_representation(values) -> None:
    """Validate only the theory-frozen dimensional contract."""
    if len(values) != REPRESENTATION_DIM:
        raise ValueError("Struct3D v4.0 representation must have 23 dimensions")
    for value in values:
        if float(value) != float(value):
            raise ValueError("representation cannot contain NaN")
