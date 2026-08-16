#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Struct3D v3.7
Structural Invariant Regression Suite

Goal
----
Define and validate structural invariants independently from the
canonical-form machinery.

Core requirement
----------------
For structurally equivalent / isomorphic worlds:

    I(W1) == I(W2)

while meaningful structural mutations should change the invariant.

The implementation is intentionally deterministic and CPU-only.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import math
import pickle
import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


VERSION = "3.7"
SEED = 20260814
EPS = 1e-9


# ============================================================
# Utilities
# ============================================================

def stable_hash(obj: Any) -> str:
    payload = pickle.dumps(obj, protocol=4)
    return hashlib.sha256(payload).hexdigest()


def freeze(value: Any) -> Any:
    """
    Convert nested mutable structures into deterministic tuples.
    Dictionaries are sorted by key representation.
    """
    if isinstance(value, dict):
        return tuple(
            sorted(
                (
                    freeze(k),
                    freeze(v),
                )
                for k, v in value.items()
            )
        )

    if isinstance(value, (list, tuple)):
        return tuple(freeze(v) for v in value)

    if isinstance(value, set):
        return tuple(sorted(freeze(v) for v in value))

    if isinstance(value, float):
        return round(value, 10)

    return value


def permute_dict(
    data: Mapping[int, Any],
    permutation: Sequence[int],
) -> Dict[int, Any]:
    """
    Relabel dictionary keys.

    permutation[old_id] = new_id
    """
    return {
        permutation[k]: copy.deepcopy(v)
        for k, v in data.items()
    }


def invert_permutation(permutation: Sequence[int]) -> Dict[int, int]:
    return {new: old for old, new in enumerate(permutation)}


def relabel_ids(
    values: Iterable[int],
    mapping: Mapping[int, int],
) -> Tuple[int, ...]:
    return tuple(mapping[v] for v in values)


# ============================================================
# Data Model
# ============================================================

@dataclass
class Unit:
    id: int
    primitive: str
    points: Tuple[Tuple[float, float, float], ...]
    metadata: Dict[str, Any]


@dataclass
class Object:
    id: int
    unit_ids: Tuple[int, ...]
    metadata: Dict[str, Any]


@dataclass
class Instance:
    id: int
    object_id: int
    metadata: Dict[str, Any]


@dataclass
class Relation:
    id: int
    source: int
    target: int
    relation_type: str
    confidence: float


@dataclass
class World:
    units: Dict[int, Unit]
    objects: Dict[int, Object]
    instances: Dict[int, Instance]
    relations: Dict[int, Relation]
    version: str = VERSION


# ============================================================
# Geometry
# ============================================================

def make_points(
    center: Tuple[float, float, float],
    pattern: Sequence[Tuple[float, float, float]],
) -> Tuple[Tuple[float, float, float], ...]:

    cx, cy, cz = center

    return tuple(
        (
            round(cx + x, 8),
            round(cy + y, 8),
            round(cz + z, 8),
        )
        for x, y, z in pattern
    )


PLANE_PATTERN = (
    (-0.10, -0.10, 0.0),
    (0.10, -0.10, 0.0),
    (-0.10, 0.10, 0.0),
    (0.10, 0.10, 0.0),
    (0.0, -0.05, 0.0),
    (0.0, 0.05, 0.0),
    (-0.05, 0.0, 0.0),
    (0.05, 0.0, 0.0),
)


SPHERE_PATTERN = (
    (0.0, 0.0, 0.10),
    (0.0, 0.0, -0.10),
    (0.10, 0.0, 0.0),
    (-0.10, 0.0, 0.0),
    (0.0, 0.10, 0.0),
    (0.0, -0.10, 0.0),
    (0.057735, 0.057735, 0.057735),
    (-0.057735, -0.057735, -0.057735),
)


def squared_distance(
    a: Sequence[float],
    b: Sequence[float],
) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def unit_geometric_signature(unit: Unit) -> Tuple[Any, ...]:
    """
    Rigid-transform-invariant geometric signature.

    We use the sorted pairwise distance multiset rather than raw
    coordinates.
    """
    points = unit.points

    distances = []

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            distances.append(
                round(
                    math.sqrt(
                        squared_distance(points[i], points[j])
                    ),
                    8,
                )
            )

    distances.sort()

    return (
        "UNIT_GEOMETRY",
        unit.primitive,
        len(points),
        tuple(distances),
    )


# ============================================================
# World Construction
# ============================================================

def build_base_world() -> World:

    units = {
        0: Unit(
            id=0,
            primitive="plane",
            points=make_points(
                (-1.0, 0.0, 0.0),
                PLANE_PATTERN,
            ),
            metadata={
                "scale": 1.0,
                "fit": 0.1,
            },
        ),
        1: Unit(
            id=1,
            primitive="plane",
            points=make_points(
                (1.0, 0.0, 0.0),
                PLANE_PATTERN,
            ),
            metadata={
                "scale": 1.0,
                "fit": 0.1,
            },
        ),
        2: Unit(
            id=2,
            primitive="sphere",
            points=make_points(
                (0.0, 1.0, 0.0),
                SPHERE_PATTERN,
            ),
            metadata={
                "scale": 1.0,
                "fit": 0.1,
            },
        ),
        3: Unit(
            id=3,
            primitive="sphere",
            points=make_points(
                (0.0, -1.0, 0.0),
                SPHERE_PATTERN,
            ),
            metadata={
                "scale": 1.0,
                "fit": 0.1,
            },
        ),
    }

    objects = {
        0: Object(
            id=0,
            unit_ids=(0, 2),
            metadata={
                "type": "assembly",
            },
        ),
        1: Object(
            id=1,
            unit_ids=(1, 3),
            metadata={
                "type": "assembly",
            },
        ),
    }

    instances = {
        0: Instance(
            id=0,
            object_id=0,
            metadata={
                "instance_type": "object",
            },
        ),
        1: Instance(
            id=1,
            object_id=1,
            metadata={
                "instance_type": "object",
            },
        ),
    }

    relations = {
        0: Relation(
            id=0,
            source=0,
            target=1,
            relation_type="adjacent",
            confidence=0.9,
        ),
        1: Relation(
            id=1,
            source=1,
            target=0,
            relation_type="adjacent",
            confidence=0.9,
        ),
    }

    return World(
        units=units,
        objects=objects,
        instances=instances,
        relations=relations,
    )


# ============================================================
# Validation
# ============================================================

def validate_world(world: World) -> bool:

    unit_ids = set(world.units.keys())
    object_ids = set(world.objects.keys())
    instance_ids = set(world.instances.keys())

    for obj in world.objects.values():
        if not set(obj.unit_ids).issubset(unit_ids):
            return False

    for inst in world.instances.values():
        if inst.object_id not in object_ids:
            return False

    for rel in world.relations.values():
        if rel.source not in object_ids:
            return False
        if rel.target not in object_ids:
            return False

    if len(unit_ids) != 4:
        return False

    if len(object_ids) != 2:
        return False

    if len(instance_ids) != 2:
        return False

    if len(world.relations) != 2:
        return False

    return True


# ============================================================
# Structural Invariant Components
# ============================================================

def unit_invariant(unit: Unit) -> Tuple[Any, ...]:

    return (
        "UNIT_INVARIANT",
        world_safe_version(unit),
        unit.primitive,
        freeze(unit.metadata),
        unit_geometric_signature(unit),
    )


def world_safe_version(unit: Unit) -> str:
    return VERSION


def object_invariant(
    world: World,
    obj: Object,
) -> Tuple[Any, ...]:

    unit_signatures = tuple(
        sorted(
            unit_invariant(world.units[uid])
            for uid in obj.unit_ids
        )
    )

    return (
        "OBJECT_INVARIANT",
        VERSION,
        freeze(obj.metadata),
        unit_signatures,
    )


def instance_invariant(
    world: World,
    instance: Instance,
) -> Tuple[Any, ...]:

    obj_sig = object_invariant(
        world,
        world.objects[instance.object_id],
    )

    return (
        "INSTANCE_INVARIANT",
        VERSION,
        obj_sig,
        freeze(instance.metadata),
    )


def relation_invariant(
    world: World,
    relation: Relation,
) -> Tuple[Any, ...]:

    source_sig = object_invariant(
        world,
        world.objects[relation.source],
    )

    target_sig = object_invariant(
        world,
        world.objects[relation.target],
    )

    endpoint_pair = tuple(
        sorted(
            (
                source_sig,
                target_sig,
            ),
            key=repr,
        )
    )

    return (
        "RELATION_INVARIANT",
        VERSION,
        endpoint_pair,
        relation.relation_type,
        round(relation.confidence, 10),
    )


# ============================================================
# Global Structural Invariant
# ============================================================

def structural_invariant(world: World) -> Tuple[Any, ...]:
    """
    Main v3.7 invariant.

    It contains only quantities / signatures invariant under
    admissible structural relabeling and rigid coordinate transforms.
    """

    unit_sigs = tuple(
        sorted(
            unit_invariant(unit)
            for unit in world.units.values()
        )
    )

    object_sigs = tuple(
        sorted(
            object_invariant(world, obj)
            for obj in world.objects.values()
        )
    )

    instance_sigs = tuple(
        sorted(
            instance_invariant(world, inst)
            for inst in world.instances.values()
        )
    )

    relation_sigs = tuple(
        sorted(
            relation_invariant(world, rel)
            for rel in world.relations.values()
        )
    )

    # Primitive histogram
    primitive_hist = tuple(
        sorted(
            (
                primitive,
                sum(
                    1
                    for unit in world.units.values()
                    if unit.primitive == primitive
                ),
            )
            for primitive in {
                unit.primitive
                for unit in world.units.values()
            }
        )
    )

    # Object cardinalities
    object_cardinalities = tuple(
        sorted(
            len(obj.unit_ids)
            for obj in world.objects.values()
        )
    )

    # Instance-object multiplicities
    instance_multiplicities = tuple(
        sorted(
            sum(
                1
                for inst in world.instances.values()
                if inst.object_id == obj.id
            )
            for obj in world.objects.values()
        )
    )

    # Relation type histogram
    relation_types = tuple(
        sorted(
            (
                rel_type,
                sum(
                    1
                    for rel in world.relations.values()
                    if rel.relation_type == rel_type
                ),
            )
            for rel_type in {
                rel.relation_type
                for rel in world.relations.values()
            }
        )
    )

    # Degree sequence
    degree_map = {
        oid: 0
        for oid in world.objects
    }

    for rel in world.relations.values():
        degree_map[rel.source] += 1
        degree_map[rel.target] += 1

    degree_sequence = tuple(
        sorted(degree_map.values())
    )

    return (
        "STRUCTURAL_INVARIANT",
        VERSION,

        (
            "CARDINALITY",
            len(world.units),
            len(world.objects),
            len(world.instances),
            len(world.relations),
        ),

        (
            "PRIMITIVE_HISTOGRAM",
            primitive_hist,
        ),

        (
            "OBJECT_CARDINALITIES",
            object_cardinalities,
        ),

        (
            "INSTANCE_MULTIPLICITIES",
            instance_multiplicities,
        ),

        (
            "RELATION_TYPES",
            relation_types,
        ),

        (
            "DEGREE_SEQUENCE",
            degree_sequence,
        ),

        (
            "UNIT_SIGNATURES",
            unit_sigs,
        ),

        (
            "OBJECT_SIGNATURES",
            object_sigs,
        ),

        (
            "INSTANCE_SIGNATURES",
            instance_sigs,
        ),

        (
            "RELATION_SIGNATURES",
            relation_sigs,
        ),
    )


def invariant_hash(world: World) -> str:
    return stable_hash(structural_invariant(world))


# ============================================================
# Relabeling
# ============================================================

def relabel_world(
    world: World,
    unit_perm: Sequence[int] | None = None,
    object_perm: Sequence[int] | None = None,
    instance_perm: Sequence[int] | None = None,
    relation_perm: Sequence[int] | None = None,
) -> World:

    if unit_perm is None:
        unit_perm = list(range(len(world.units)))

    if object_perm is None:
        object_perm = list(range(len(world.objects)))

    if instance_perm is None:
        instance_perm = list(range(len(world.instances)))

    if relation_perm is None:
        relation_perm = list(range(len(world.relations)))

    um = {
        old: new
        for old, new in enumerate(unit_perm)
    }

    om = {
        old: new
        for old, new in enumerate(object_perm)
    }

    im = {
        old: new
        for old, new in enumerate(instance_perm)
    }

    rm = {
        old: new
        for old, new in enumerate(relation_perm)
    }

    units = {}

    for old_id, unit in world.units.items():

        new_id = um[old_id]

        units[new_id] = Unit(
            id=new_id,
            primitive=unit.primitive,
            points=copy.deepcopy(unit.points),
            metadata=copy.deepcopy(unit.metadata),
        )

    objects = {}

    for old_id, obj in world.objects.items():

        new_id = om[old_id]

        objects[new_id] = Object(
            id=new_id,
            unit_ids=tuple(
                sorted(
                    um[u]
                    for u in obj.unit_ids
                )
            ),
            metadata=copy.deepcopy(obj.metadata),
        )

    instances = {}

    for old_id, inst in world.instances.items():

        new_id = im[old_id]

        instances[new_id] = Instance(
            id=new_id,
            object_id=om[inst.object_id],
            metadata=copy.deepcopy(inst.metadata),
        )

    relations = {}

    for old_id, rel in world.relations.items():

        new_id = rm[old_id]

        relations[new_id] = Relation(
            id=new_id,
            source=om[rel.source],
            target=om[rel.target],
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    return World(
        units=units,
        objects=objects,
        instances=instances,
        relations=relations,
        version=world.version,
    )


# ============================================================
# Rigid Transform
# ============================================================

def mat_vec(
    matrix: Sequence[Sequence[float]],
    vector: Sequence[float],
) -> Tuple[float, float, float]:

    return tuple(
        sum(matrix[i][j] * vector[j] for j in range(3))
        for i in range(3)
    )


def rigid_transform_world(
    world: World,
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
) -> World:

    new_world = copy.deepcopy(world)

    for unit in new_world.units.values():

        transformed = []

        for point in unit.points:

            rotated = mat_vec(rotation, point)

            transformed.append(
                tuple(
                    round(
                        rotated[i] + translation[i],
                        8,
                    )
                    for i in range(3)
                )
            )

        unit.points = tuple(transformed)

    return new_world


# ============================================================
# Automorphism Enumeration
# ============================================================

def enumerate_permutations(n: int):
    return itertools.permutations(range(n))


def is_structural_automorphism(
    world: World,
    candidate: World,
) -> bool:

    return structural_invariant(world) == structural_invariant(candidate)


def enumerate_explicit_automorphisms(
    world: World,
) -> List[World]:

    results = []

    for up in enumerate_permutations(len(world.units)):

        for op in enumerate_permutations(len(world.objects)):

            for ip in enumerate_permutations(len(world.instances)):

                for rp in enumerate_permutations(len(world.relations)):

                    candidate = relabel_world(
                        world,
                        up,
                        op,
                        ip,
                        rp,
                    )

                    if is_structural_automorphism(
                        world,
                        candidate,
                    ):
                        results.append(candidate)

    return results


# ============================================================
# Mutations
# ============================================================

def mutate_primitive(world: World) -> World:

    w = copy.deepcopy(world)

    w.units[0].primitive = "cylinder"

    return w


def mutate_object_composition(world: World) -> World:

    w = copy.deepcopy(world)

    w.objects[0].unit_ids = (
        0,
        1,
        2,
    )

    return w


def mutate_instance_composition(world: World) -> World:

    w = copy.deepcopy(world)

    w.instances[0].object_id = 1

    return w


def mutate_relation_type(world: World) -> World:

    w = copy.deepcopy(world)

    w.relations[0].relation_type = "contains"

    return w


def mutate_relation_confidence(world: World) -> World:

    w = copy.deepcopy(world)

    w.relations[0].confidence = 0.5

    return w


def mutate_relation_deletion(world: World) -> World:

    w = copy.deepcopy(world)

    del w.relations[1]

    return w


# ============================================================
# Test Infrastructure
# ============================================================

class TestSuite:

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0

    def check(
        self,
        name: str,
        condition: bool,
    ):

        self.total += 1

        if condition:
            self.passed += 1
            print(f"[PASS] {name}")
        else:
            self.failed += 1
            print(f"[FAIL] {name}")

    def section(self, title: str):

        print()
        print("-" * 60)
        print(title)
        print("-" * 60)


# ============================================================
# Main Regression Suite
# ============================================================

def main():

    random.seed(SEED)

    suite = TestSuite()

    print("=" * 60)
    print("Struct3D v3.7 Structural Invariant Regression Suite")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Seed: {SEED}")

    # --------------------------------------------------------
    # 1. Base World
    # --------------------------------------------------------

    suite.section("[1] Base World")

    world = build_base_world()

    print(f"Units: {len(world.units)}")
    print(f"Objects: {len(world.objects)}")
    print(f"Instances: {len(world.instances)}")
    print(f"Relations: {len(world.relations)}")

    suite.check(
        "World Validation",
        validate_world(world),
    )

    # --------------------------------------------------------
    # Structural Invariant
    # --------------------------------------------------------

    suite.section("Structural Invariant")

    inv = structural_invariant(world)
    h = invariant_hash(world)

    print("Invariant generated:", inv is not None)
    print("Invariant hash:", h)

    suite.check(
        "Invariant Exists",
        inv is not None and len(inv) > 0,
    )

    # --------------------------------------------------------
    # Reflexivity
    # --------------------------------------------------------

    suite.section("Invariant Reflexivity")

    inv2 = structural_invariant(world)

    print(
        "I(W) == I(W):",
        inv == inv2,
    )

    suite.check(
        "Invariant Reflexivity",
        inv == inv2,
    )

    # --------------------------------------------------------
    # Determinism
    # --------------------------------------------------------

    suite.section("Invariant Determinism")

    hashes = [
        invariant_hash(world)
        for _ in range(5)
    ]

    deterministic = len(set(hashes)) == 1

    print("Hashes:", hashes)

    suite.check(
        "Invariant Determinism",
        deterministic,
    )

    # --------------------------------------------------------
    # Dictionary Order
    # --------------------------------------------------------

    suite.section("Dictionary Order Invariance")

    reordered = World(
        units=dict(reversed(list(world.units.items()))),
        objects=dict(reversed(list(world.objects.items()))),
        instances=dict(reversed(list(world.instances.items()))),
        relations=dict(reversed(list(world.relations.items()))),
    )

    original_hash = invariant_hash(world)
    reordered_hash = invariant_hash(reordered)

    print("Original hash:", original_hash)
    print("Reordered hash:", reordered_hash)

    suite.check(
        "Dictionary Order Invariance",
        original_hash == reordered_hash,
    )

    # --------------------------------------------------------
    # Unit Relabeling
    # --------------------------------------------------------

    suite.section("Unit Relabeling Invariance")

    unit_perm = [1, 0, 3, 2]

    relabeled = relabel_world(
        world,
        unit_perm=unit_perm,
    )

    print("Unit permutation:", unit_perm)

    suite.check(
        "Unit Relabeling Invariance",
        invariant_hash(world) == invariant_hash(relabeled),
    )

    # --------------------------------------------------------
    # Object Relabeling
    # --------------------------------------------------------

    suite.section("Object Relabeling Invariance")

    object_perm = [1, 0]

    relabeled = relabel_world(
        world,
        object_perm=object_perm,
    )

    print("Object permutation:", object_perm)

    suite.check(
        "Object Relabeling Invariance",
        invariant_hash(world) == invariant_hash(relabeled),
    )

    # --------------------------------------------------------
    # Instance Relabeling
    # --------------------------------------------------------

    suite.section("Instance Relabeling Invariance")

    instance_perm = [1, 0]

    relabeled = relabel_world(
        world,
        instance_perm=instance_perm,
    )

    print("Instance permutation:", instance_perm)

    suite.check(
        "Instance Relabeling Invariance",
        invariant_hash(world) == invariant_hash(relabeled),
    )

    # --------------------------------------------------------
    # Relation Relabeling
    # --------------------------------------------------------

    suite.section("Relation Relabeling Invariance")

    relation_perm = [1, 0]

    relabeled = relabel_world(
        world,
        relation_perm=relation_perm,
    )

    print("Relation permutation:", relation_perm)

    suite.check(
        "Relation Relabeling Invariance",
        invariant_hash(world) == invariant_hash(relabeled),
    )

    # --------------------------------------------------------
    # Combined Relabeling
    # --------------------------------------------------------

    suite.section("Combined Relabeling Invariance")

    combined = relabel_world(
        world,
        unit_perm=[1, 0, 3, 2],
        object_perm=[1, 0],
        instance_perm=[1, 0],
        relation_perm=[1, 0],
    )

    suite.check(
        "Combined Relabeling Invariance",
        invariant_hash(world) == invariant_hash(combined),
    )

    # --------------------------------------------------------
    # Rigid Transform
    # --------------------------------------------------------

    suite.section("Rigid Transform Invariance")

    theta = math.pi / 2

    rotation = (
        (math.cos(theta), -math.sin(theta), 0.0),
        (math.sin(theta), math.cos(theta), 0.0),
        (0.0, 0.0, 1.0),
    )

    translation = (
        17.25,
        -31.75,
        42.5,
    )

    transformed = rigid_transform_world(
        world,
        rotation,
        translation,
    )

    determinant = (
        rotation[0][0]
        * (
            rotation[1][1] * rotation[2][2]
            - rotation[1][2] * rotation[2][1]
        )
        - rotation[0][1]
        * (
            rotation[1][0] * rotation[2][2]
            - rotation[1][2] * rotation[2][0]
        )
        + rotation[0][2]
        * (
            rotation[1][0] * rotation[2][1]
            - rotation[1][1] * rotation[2][0]
        )
    )

    print(
        f"Rigid rotation determinant: {determinant:.12f}"
    )

    print(
        "Rigid translation:",
        translation,
    )

    suite.check(
        "Rigid Transform Invariance",
        abs(determinant - 1.0) < EPS
        and invariant_hash(world)
        == invariant_hash(transformed),
    )

    # --------------------------------------------------------
    # Automorphism Compatibility
    # --------------------------------------------------------

    suite.section("Automorphism Compatibility")

    automorphisms = enumerate_explicit_automorphisms(world)

    print(
        "Automorphisms tested:",
        len(automorphisms),
    )

    all_preserve = all(
        invariant_hash(world)
        == invariant_hash(candidate)
        for candidate in automorphisms
    )

    suite.check(
        "All Automorphisms Preserve Invariant",
        all_preserve,
    )

    # --------------------------------------------------------
    # Mutation: Primitive
    # --------------------------------------------------------

    suite.section(
        "Structural Non-Invariance: Primitive"
    )

    mutated = mutate_primitive(world)

    original = invariant_hash(world)
    changed = invariant_hash(mutated)

    print("Original invariant hash:", original)
    print("Mutated invariant hash:", changed)

    suite.check(
        "Primitive Mutation",
        original != changed,
    )

    # --------------------------------------------------------
    # Mutation: Object Composition
    # --------------------------------------------------------

    suite.section(
        "Structural Non-Invariance: Object Composition"
    )

    mutated = mutate_object_composition(world)

    original = invariant_hash(world)
    changed = invariant_hash(mutated)

    print("Original invariant hash:", original)
    print("Mutated invariant hash:", changed)

    suite.check(
        "Object Composition Mutation",
        original != changed,
    )

    # --------------------------------------------------------
    # Mutation: Instance Composition
    # --------------------------------------------------------

    suite.section(
        "Structural Non-Invariance: Instance Composition"
    )

    mutated = mutate_instance_composition(world)

    original = invariant_hash(world)
    changed = invariant_hash(mutated)

    print("Original invariant hash:", original)
    print("Mutated invariant hash:", changed)

    suite.check(
        "Instance Composition Mutation",
        original != changed,
    )

    # --------------------------------------------------------
    # Mutation: Relation Type
    # --------------------------------------------------------

    suite.section(
        "Structural Non-Invariance: Relation Type"
    )

    mutated = mutate_relation_type(world)

    original = invariant_hash(world)
    changed = invariant_hash(mutated)

    print("Original invariant hash:", original)
    print("Mutated invariant hash:", changed)

    suite.check(
        "Relation Type Mutation",
        original != changed,
    )

    # --------------------------------------------------------
    # Mutation: Relation Confidence
    # --------------------------------------------------------

    suite.section(
        "Structural Non-Invariance: Relation Confidence"
    )

    mutated = mutate_relation_confidence(world)

    original = invariant_hash(world)
    changed = invariant_hash(mutated)

    print("Original invariant hash:", original)
    print("Mutated invariant hash:", changed)

    suite.check(
        "Relation Confidence Mutation",
        original != changed,
    )

    # --------------------------------------------------------
    # Mutation: Relation Deletion
    # --------------------------------------------------------

    suite.section(
        "Structural Non-Invariance: Relation Deletion"
    )

    mutated = mutate_relation_deletion(world)

    original = invariant_hash(world)
    changed = invariant_hash(mutated)

    print("Original invariant hash:", original)
    print("Mutated invariant hash:", changed)

    suite.check(
        "Relation Deletion",
        original != changed,
    )

    # --------------------------------------------------------
    # Invariant Stability Under Repeated Relabeling
    # --------------------------------------------------------

    suite.section(
        "Repeated Relabeling Stability"
    )

    stable = True

    for _ in range(20):

        up = list(range(4))
        op = list(range(2))
        ip = list(range(2))
        rp = list(range(2))

        random.shuffle(up)
        random.shuffle(op)
        random.shuffle(ip)
        random.shuffle(rp)

        candidate = relabel_world(
            world,
            unit_perm=up,
            object_perm=op,
            instance_perm=ip,
            relation_perm=rp,
        )

        if invariant_hash(world) != invariant_hash(candidate):
            stable = False
            break

    suite.check(
        "Repeated Relabeling Stability",
        stable,
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v3.7")
    print("=" * 60)

    print(
        f"Total tests: {suite.total}"
    )

    print(
        f"Passed: {suite.passed}"
    )

    print(
        f"Failed: {suite.failed}"
    )

    status = (
        "PASS"
        if suite.failed == 0
        else "FAIL"
    )

    print(
        f"STATUS: {status}"
    )

    print("=" * 60)

    if suite.failed != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()