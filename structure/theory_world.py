"""Theory-facing Structural World container.

Frozen definition:
    W = (U, R, Phi)

The graph representation is the explicit structural graph
    G = (V, E)
with V indexed by world units and E copied exactly from world relations.
No edges are inferred from unit attributes or primitive equality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation


@dataclass(frozen=True)
class StructuralGraph:
    """Explicit graph view G=(V,E) of a StructuralWorld."""

    vertices: Tuple[int, ...]
    edges: Tuple[StructuralRelation, ...]


@dataclass(frozen=True)
class StructuralWorld:
    units: Tuple[TheoryUnit, ...]
    relations: Tuple[StructuralRelation, ...]
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        n = len(self.units)
        for relation in self.relations:
            if not (0 <= relation.source < n and 0 <= relation.target < n):
                raise ValueError("relation references a unit outside the world")

    @property
    def unit_count(self) -> int:
        return len(self.units)

    @property
    def relation_count(self) -> int:
        return len(self.relations)

    @property
    def graph(self) -> StructuralGraph:
        """Return the explicit graph view; never infer additional edges."""
        return StructuralGraph(
            vertices=tuple(range(self.unit_count)),
            edges=self.relations,
        )
