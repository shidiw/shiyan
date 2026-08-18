"""Exact canonical form for finite Structural Worlds.

For a finite world, canonicalization is defined as the lexicographically
minimal serialization over all unit relabelings. This is an exact finite
definition, not a heuristic graph hash. The implementation uses exhaustive
permutations and therefore is intended for validation/small structural worlds;
large-world optimization is a separate engineering problem.
"""

from __future__ import annotations

from itertools import permutations
from typing import Any, Tuple

from .theory_world import StructuralWorld


def _freeze(value: Any):
    if isinstance(value, dict):
        return tuple(sorted((str(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted(_freeze(v) for v in value))
    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)


def _node_signature(unit) -> Tuple[Any, ...]:
    return (
        tuple(unit.indices),
        unit.primitive,
        _freeze(unit.attributes),
    )


def canonical_form(world: StructuralWorld):
    """Return a label-independent exact canonical tuple for a finite world."""
    n = len(world.units)
    node_sig = tuple(_node_signature(u) for u in world.units)
    relation_sig = tuple(
        sorted(
            (
                r.source,
                r.target,
                r.relation_type,
                _freeze(r.evidence),
            )
            for r in world.relations
        )
    )

    best = None
    for perm in permutations(range(n)):
        inverse = {old: new for new, old in enumerate(perm)}
        nodes = tuple(node_sig[old] for old in perm)
        relations = tuple(
            sorted(
                (
                    inverse[s],
                    inverse[t],
                    typ,
                    evidence,
                )
                for s, t, typ, evidence in relation_sig
            )
        )
        candidate = (nodes, relations, _freeze(world.attributes))
        if best is None or candidate < best:
            best = candidate
    return best


def structurally_equivalent(a: StructuralWorld, b: StructuralWorld) -> bool:
    return canonical_form(a) == canonical_form(b)
