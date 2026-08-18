"""Formal structural graph from the frozen Struct3D theory.

Mathematical definition:
    G = (V, E)
    V = {u_1, ..., u_K}
    E = {(u_i, u_j, r_ij)}

A StructuralWorld additionally carries structural attributes Phi. This module
keeps the graph layer explicit instead of treating World as an implicit graph
container.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation


@dataclass(frozen=True)
class StructuralGraph:
    """Finite graph G=(V,E) over an explicit ordered unit set."""

    vertices: Tuple[TheoryUnit, ...]
    edges: Tuple[StructuralRelation, ...]

    def __post_init__(self) -> None:
        n = len(self.vertices)
        for edge in self.edges:
            if not (0 <= edge.source < n and 0 <= edge.target < n):
                raise ValueError("graph edge references a vertex outside V")

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def as_world_components(self):
        """Return the exact (U,R) components used by W=(U,R,Phi)."""
        return self.vertices, self.edges
