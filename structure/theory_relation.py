"""Theory-facing structural relations.

Frozen theory statement:
    r_ij is a relation between structural units and its evidence may depend on
    geometry, boundary and spatial configuration.

This module intentionally does not assign relation types from thresholds or
primitive equality. Legacy relation inference remains in relation.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple

from .theory_core import TheoryUnit


@dataclass(frozen=True)
class StructuralRelation:
    """A typed relation record r_ij with explicit evidence/provenance."""

    source: int
    target: int
    relation_type: str
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source == self.target:
            raise ValueError("A structural relation requires two distinct units")
        if not self.relation_type:
            raise ValueError("relation_type must be non-empty")

    @property
    def units(self) -> Tuple[int, int]:
        return (self.source, self.target)


@dataclass(frozen=True)
class StructuralRelations:
    """A finite relation set over a fixed unit index domain."""

    relations: Tuple[StructuralRelation, ...]
    unit_count: int

    def __post_init__(self) -> None:
        if self.unit_count < 0:
            raise ValueError("unit_count must be non-negative")
        for relation in self.relations:
            if not (0 <= relation.source < self.unit_count):
                raise ValueError("relation source outside unit domain")
            if not (0 <= relation.target < self.unit_count):
                raise ValueError("relation target outside unit domain")


def relation_from_units(
    source: TheoryUnit,
    target: TheoryUnit,
    source_id: int,
    target_id: int,
    relation_type: str,
    evidence: Optional[Mapping[str, Any]] = None,
) -> StructuralRelation:
    """Construct a relation without deriving it from an unapproved heuristic."""
    return StructuralRelation(
        source=source_id,
        target=target_id,
        relation_type=relation_type,
        evidence=dict(evidence or {}),
    )
