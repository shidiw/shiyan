"""Explicit partition-cell -> Structural Unit materialization boundary.

At the current frozen theory level a valid partition already consists of
StructuralUnit cells. Materialization is therefore an identity construction,
not a hidden discovery, thresholding, primitive-fitting, or merging step.
"""

from __future__ import annotations

from typing import Tuple

from .theory_core import Partition, StructuralUnit


def materialize_units(partition: Partition) -> Tuple[StructuralUnit, ...]:
    """Expose the Units represented by a valid partition without mutation."""
    if not partition.is_partition:
        raise ValueError("Only a valid partition can be materialized")
    return partition.units
