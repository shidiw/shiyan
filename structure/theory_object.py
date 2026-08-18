"""Derived Object construction over the frozen Struct3D core.

IMPORTANT THEORY STATUS
-----------------------
The current Struct3D mathematical specification defines

    W = (U, R, Phi)

and defines Units, Relations, Graphs, relabeling, canonical form,
invariance, representation, distance and matching.  It does *not* give a
formal Definition/Theorem that names Object or fixes a unique Object
emergence operator.

Therefore this module MUST NOT be read as a new mathematical axiom.
``assemble_objects`` is a derived engineering construction that is kept
explicit so that later theory work can replace or formally justify it
without changing the frozen core.

The current engineering rule is deliberately conservative:

    O_derived = connected components of (U, R_assembly)

where ``R_assembly`` is supplied explicitly by the caller.  No primitive
label, distance threshold, proximity heuristic, or legacy relation inference
is used here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation


THEORY_STATUS = "DERIVED_ENGINEERING_CONSTRUCTION"


@dataclass(frozen=True)
class StructuralObject:
    """A derived object represented by the Unit indices it assembles."""

    unit_ids: Tuple[int, ...]
    attributes: Mapping[str, object]

    def __post_init__(self) -> None:
        ids = tuple(sorted(set(self.unit_ids)))
        if not ids:
            raise ValueError("Object must contain at least one unit")
        if ids != self.unit_ids:
            raise ValueError("Object unit_ids must be unique and sorted")


def assemble_objects(
    units: Tuple[TheoryUnit, ...],
    relations: Tuple[StructuralRelation, ...],
) -> Tuple[StructuralObject, ...]:
    """Construct derived Objects from an explicit assembly relation subset.

    This function is intentionally an engineering-layer operator, not a
    theorem of the current mathematical specification.  Only relations whose
    type is exactly ``"assembly"`` participate.  All relation endpoints are
    checked against the supplied Unit domain.
    """
    n = len(units)
    if n == 0:
        return tuple()

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


__all__ = ["THEORY_STATUS", "StructuralObject", "assemble_objects"]
