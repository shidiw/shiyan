"""Theory-facing object construction.

The mathematical specification defines the Structural World as
W = (U, R, Phi).  Object is therefore treated here as a derived structural
construction from U and an explicitly designated subset of R; it is not
silently added as a fourth coordinate of W.

The construction used by this module is:
    O = connected components of (U, R_assembly)
where R_assembly is supplied explicitly by the caller.  The module does not
infer assembly from primitive labels, distance thresholds, or other legacy
heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation


@dataclass(frozen=True)
class StructuralObject:
    """A derived object represented by the Unit indices it assembles."""

    unit_ids: Tuple[int, ...]
    attributes: Mapping[str, object]

    def __post_init__(self) -> None:
        ids = tuple(sorted(set(self.unit_ids)))
        if ids != self.unit_ids:
            raise ValueError("Object unit_ids must be unique and sorted")


def assemble_objects(
    units: Tuple[TheoryUnit, ...],
    relations: Tuple[StructuralRelation, ...],
) -> Tuple[StructuralObject, ...]:
    """Construct Objects as connected components of explicit assembly edges.

    Only relations whose type is exactly ``"assembly"`` participate.  This is
    deliberately an explicit relation-domain choice: no primitive equality,
    proximity threshold, or hidden heuristic is used to create an object.
    """
    n = len(units)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for relation in relations:
        if not (0 <= relation.source < n and 0 <= relation.target < n):
            raise ValueError("relation references an invalid unit")
        if relation.relation_type == "assembly":
            union(relation.source, relation.target)

    groups = {}
    for idx in range(n):
        groups.setdefault(find(idx), []).append(idx)

    return tuple(
        StructuralObject(tuple(ids), {})
        for ids in sorted(groups.values(), key=lambda ids: ids[0])
    )
