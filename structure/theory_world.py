"""Theory-facing Structural World container.

Frozen definition:
    W = (U, R, Phi)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation


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
