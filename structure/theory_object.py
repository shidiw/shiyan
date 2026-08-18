"""Theory-facing object assembly.

An Object is the unit-level component induced by an explicitly supplied
assembly relation. The component operation is a mathematical construction;
the module does not decide which relations are assembly relations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation


@dataclass(frozen=True)
class StructuralObject:
    unit_ids: Tuple[int, ...]
    attributes: Mapping[str, object]


def assemble_objects(
    units: Tuple[TheoryUnit, ...],
    relations: Tuple[StructuralRelation, ...],
) -> Tuple[StructuralObject, ...]:
    """Form connected components of the explicitly supplied assembly graph.

    A relation is considered an assembly relation only when its type is
    explicitly ``"assembly"``. This is an interface convention, not a claim
    about how the formal theory must classify geometric relations.
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
        if relation.relation_type != "assembly":
            continue
        if not (0 <= relation.source < n and 0 <= relation.target < n):
            raise ValueError("assembly relation references an invalid unit")
        union(relation.source, relation.target)

    groups = {}
    for idx in range(n):
        groups.setdefault(find(idx), []).append(idx)

    return tuple(
        StructuralObject(tuple(ids), {})
        for ids in sorted(groups.values(), key=lambda ids: ids[0])
    )
