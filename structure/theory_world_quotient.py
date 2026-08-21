"""Structural World quotient and quotient-space representation contracts.

Frozen chain:
    X -> Gamma(X) -> P* -> U -> R -> W=(U,R,Phi) -> [W].

The quotient representative is index-free: observation indices and current
Unit ordering are removed. Observation-derived theta is the Unit key, while
explicit relations are transported between those keys.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from .theory_observation_theta import theta_signature
from .theory_relation import StructuralRelation
from .theory_world import StructuralWorld


def _freeze(value: Any):
    if isinstance(value, Mapping):
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


def _unit_quotient_key(unit):
    """Return an index-free Unit quotient representative."""
    try:
        return ("theta", _freeze(theta_signature(unit)))
    except (ValueError, TypeError):
        return ("structural", unit.primitive, _freeze(unit.attributes))


def world_quotient_form(world: StructuralWorld):
    """Return the exact finite representative of the World quotient.

    Raw support indices and current Unit ordering are deliberately absent.
    Duplicate quotient Unit keys are rejected because the frozen theta map is
    injective on the simple-observation domain.
    """
    keys = tuple(_unit_quotient_key(u) for u in world.units)
    if len(set(keys)) != len(keys):
        raise ValueError("World quotient requires distinct Unit quotient classes")

    relation_rows = []
    for relation in world.relations:
        if not (0 <= relation.source < len(keys) and 0 <= relation.target < len(keys)):
            raise ValueError("relation endpoint outside world Unit domain")
        relation_rows.append(
            (
                keys[relation.source],
                keys[relation.target],
                relation.relation_type,
                _freeze(relation.evidence),
            )
        )

    return (tuple(sorted(keys)), tuple(sorted(relation_rows)))


def world_quotient_equivalent(a: StructuralWorld, b: StructuralWorld) -> bool:
    """Define W1 ~_W W2 iff their Unit/Relation quotient forms agree."""
    return world_quotient_form(a) == world_quotient_form(b)


def world_quotient_bijection(a: StructuralWorld, b: StructuralWorld) -> dict[int, int]:
    """Return the unique Unit map induced by equality of quotient keys."""
    target = {}
    for j, unit in enumerate(b.units):
        key = _unit_quotient_key(unit)
        if key in target:
            raise ValueError("target contains duplicate Unit quotient classes")
        target[key] = j

    mapping = {}
    for i, unit in enumerate(a.units):
        key = _unit_quotient_key(unit)
        if key not in target:
            raise ValueError("Worlds have different Unit quotient classes")
        mapping[i] = target[key]

    if len(mapping) != len(b.units):
        raise ValueError("Worlds have different Unit counts")
    return mapping


def _transport_relation_signature(world: StructuralWorld, mapping: Mapping[int, int]):
    return tuple(
        sorted(
            (
                mapping[r.source],
                mapping[r.target],
                r.relation_type,
                _freeze(r.evidence),
            )
            for r in world.relations
        )
    )


def prove_structural_world_quotient(a: StructuralWorld, b: StructuralWorld) -> bool:
    """Finite proof certificate for the Structural World Quotient Theorem."""
    if not world_quotient_equivalent(a, b):
        return False
    mapping = world_quotient_bijection(a, b)
    if any(_unit_quotient_key(a.units[i]) != _unit_quotient_key(b.units[j]) for i, j in mapping.items()):
        return False
    return _transport_relation_signature(a, mapping) == tuple(
        sorted(
            (r.source, r.target, r.relation_type, _freeze(r.evidence))
            for r in b.relations
        )
    )


def quotient_representation(
    world: StructuralWorld,
    extractor: Callable[[Any], Sequence[float]],
) -> tuple[float, ...]:
    """Evaluate Phi on the quotient representative, never on raw indices."""
    return tuple(float(v) for v in extractor(world_quotient_form(world)))


def phi_well_defined_on_quotient(
    worlds: Sequence[StructuralWorld],
    extractor: Callable[[StructuralWorld], Sequence[float]],
) -> bool:
    """Finite audit that a raw-world Phi is constant on tested quotient classes."""
    values = {}
    for world in worlds:
        key = world_quotient_form(world)
        value = tuple(float(v) for v in extractor(world))
        previous = values.get(key)
        if previous is not None and previous != value:
            return False
        values[key] = value
    return True


__all__ = [
    "world_quotient_form",
    "world_quotient_equivalent",
    "world_quotient_bijection",
    "prove_structural_world_quotient",
    "quotient_representation",
    "phi_well_defined_on_quotient",
]
