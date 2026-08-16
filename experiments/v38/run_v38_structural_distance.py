#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Struct3D v3.8
Structural Distance Regression Suite

Strict version boundary:
    v3.6 -> Structural Canonical Form
    v3.7 -> Structural Invariant
    v3.8 -> Structural Distance
    v3.9 -> Structural Matching
    v4.0 -> Structural Representation
    Neural Struct3D

This file intentionally implements ONLY v3.8.

Core definition:

    D(W1, W2) = || F(W1) - F(W2) ||_2

where F(W) is a deterministic, permutation-invariant structural
signature derived from the v3.7 invariant.

Important:
    instance -> object ownership is explicitly represented.

Therefore:

    I0 -> O0
    I1 -> O1

and

    I0 -> O1
    I1 -> O1

must have positive structural distance.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Sequence, Tuple


# ============================================================
# Global configuration
# ============================================================

VERSION = "3.8"
SEED = 20260814

random.seed(SEED)


# ============================================================
# Numeric helpers
# ============================================================

EPS = 1e-12
ROUND_DIGITS = 10


def q(x: float) -> float:
    """Stable numeric quantization."""
    return round(float(x), ROUND_DIGITS)


def vector_norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) ** 2 for x in v))


def euclidean_distance(a: Sequence[float],
                       b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vector dimensions differ.")
    return vector_norm([float(x) - float(y) for x, y in zip(a, b)])


# ============================================================
# Stable serialization
# ============================================================

def freeze(obj: Any) -> Any:
    """
    Convert nested mutable structures into deterministic tuples.
    Dictionary keys are sorted.
    """
    if isinstance(obj, dict):
        return tuple(
            (k, freeze(obj[k]))
            for k in sorted(obj.keys(), key=lambda x: str(x))
        )

    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)

    if isinstance(obj, set):
        return tuple(sorted(
            (freeze(x) for x in obj),
            key=repr,
        ))

    if isinstance(obj, float):
        return q(obj)

    return obj


def stable_bytes(obj: Any) -> bytes:
    return repr(freeze(obj)).encode("utf-8")


def stable_hash(obj: Any) -> str:
    return hashlib.sha256(stable_bytes(obj)).hexdigest()


# ============================================================
# Data model
# ============================================================

@dataclass
class Unit:
    uid: int
    primitive: str
    scale: float = 1.0
    fit: float = 0.1
    points: Tuple[Tuple[float, float, float], ...] = field(default_factory=tuple)

    def signature(self) -> Tuple:
        pts = tuple(
            sorted(
                (
                    (
                        q(p[0]),
                        q(p[1]),
                        q(p[2]),
                    )
                    for p in self.points
                ),
                key=repr,
            )
        )

        # Pairwise intrinsic distances remove translation and rotation.
        distances = []
        for i in range(len(self.points)):
            for j in range(i + 1, len(self.points)):
                distances.append(
                    q(
                        euclidean_distance(
                            self.points[i],
                            self.points[j],
                        )
                    )
                )

        distances = tuple(sorted(distances))

        return (
            "UNIT",
            VERSION,
            self.primitive,
            ("scale", q(self.scale)),
            ("fit", q(self.fit)),
            ("n", len(self.points)),
            ("dist", distances),
            ("points_intrinsic", pts),
        )


@dataclass
class ObjectNode:
    oid: int
    object_type: str
    units: Tuple[int, ...] = field(default_factory=tuple)

    def signature(
        self,
        units_by_id: Dict[int, Unit],
    ) -> Tuple:
        unit_sigs = tuple(
            sorted(
                (
                    units_by_id[u].signature()
                    for u in self.units
                ),
                key=repr,
            )
        )

        return (
            "OBJECT",
            VERSION,
            self.object_type,
            unit_sigs,
        )


@dataclass
class InstanceNode:
    iid: int
    object_id: int

    def signature(
        self,
        objects_by_id: Dict[int, ObjectNode],
        units_by_id: Dict[int, Unit],
    ) -> Tuple:
        return (
            "INSTANCE",
            VERSION,
            objects_by_id[self.object_id].signature(units_by_id),
        )


@dataclass
class Relation:
    rid: int
    source_object: int
    target_object: int
    relation_type: str
    confidence: float

    def signature(
        self,
        objects_by_id: Dict[int, ObjectNode],
        units_by_id: Dict[int, Unit],
    ) -> Tuple:
        src = objects_by_id[self.source_object].signature(units_by_id)
        dst = objects_by_id[self.target_object].signature(units_by_id)

        return (
            "RELATION",
            VERSION,
            src,
            dst,
            ("type", self.relation_type),
            ("confidence", q(self.confidence)),
        )


@dataclass
class World:
    units: Dict[int, Unit]
    objects: Dict[int, ObjectNode]
    instances: Dict[int, InstanceNode]
    relations: Dict[int, Relation]

    def clone(self) -> "World":
        return copy.deepcopy(self)


# ============================================================
# Base world
# ============================================================

def make_base_world() -> World:
    """
    Four geometric units:

        U0 U1 -> plane
        U2 U3 -> sphere

    Two objects:

        O0 -> U0,U3
        O1 -> U1,U2

    Two instances:

        I0 -> O0
        I1 -> O1

    Two relations:

        O0 -> O1
        O1 -> O0
    """

    plane_a = (
        (-0.05, -0.05, 0.0),
        ( 0.05, -0.05, 0.0),
        (-0.05,  0.05, 0.0),
        ( 0.05,  0.05, 0.0),
    )

    plane_b = (
        (-0.05, -0.05, 0.0),
        ( 0.05, -0.05, 0.0),
        (-0.05,  0.05, 0.0),
        ( 0.05,  0.05, 0.0),
    )

    sphere_a = (
        (0.10, 0.00, 0.00),
        (-0.10, 0.00, 0.00),
        (0.00, 0.10, 0.00),
        (0.00, -0.10, 0.00),
    )

    sphere_b = (
        (0.10, 0.00, 0.00),
        (-0.10, 0.00, 0.00),
        (0.00, 0.10, 0.00),
        (0.00, -0.10, 0.00),
    )

    units = {
        0: Unit(0, "plane", points=plane_a),
        1: Unit(1, "plane", points=plane_b),
        2: Unit(2, "sphere", points=sphere_a),
        3: Unit(3, "sphere", points=sphere_b),
    }

    objects = {
        0: ObjectNode(
            oid=0,
            object_type="assembly",
            units=(0, 3),
        ),
        1: ObjectNode(
            oid=1,
            object_type="assembly",
            units=(1, 2),
        ),
    }

    instances = {
        0: InstanceNode(
            iid=0,
            object_id=0,
        ),
        1: InstanceNode(
            iid=1,
            object_id=1,
        ),
    }

    relations = {
        0: Relation(
            rid=0,
            source_object=0,
            target_object=1,
            relation_type="adjacent",
            confidence=0.90,
        ),
        1: Relation(
            rid=1,
            source_object=1,
            target_object=0,
            relation_type="adjacent",
            confidence=0.90,
        ),
    }

    return World(
        units=units,
        objects=objects,
        instances=instances,
        relations=relations,
    )


# ============================================================
# World validation
# ============================================================

def validate_world(world: World) -> None:
    for oid, obj in world.objects.items():
        for uid in obj.units:
            if uid not in world.units:
                raise AssertionError(
                    f"Object {oid} references missing unit {uid}"
                )

    for iid, inst in world.instances.items():
        if inst.object_id not in world.objects:
            raise AssertionError(
                f"Instance {iid} references missing object "
                f"{inst.object_id}"
            )

    for rid, rel in world.relations.items():
        if rel.source_object not in world.objects:
            raise AssertionError(
                f"Relation {rid} source missing"
            )
        if rel.target_object not in world.objects:
            raise AssertionError(
                f"Relation {rid} target missing"
            )

        if not (0.0 <= rel.confidence <= 1.0):
            raise AssertionError(
                f"Relation {rid} confidence out of range"
            )


# ============================================================
# Structural signature components
# ============================================================

def unit_multiset_signature(world: World) -> Tuple:
    return tuple(
        sorted(
            (
                unit.signature()
                for unit in world.units.values()
            ),
            key=repr,
        )
    )


def object_multiset_signature(world: World) -> Tuple:
    return tuple(
        sorted(
            (
                obj.signature(world.units)
                for obj in world.objects.values()
            ),
            key=repr,
        )
    )


def instance_signature(
    world: World,
    instance: InstanceNode,
) -> Tuple:
    """
    IMPORTANT v3.8 FIX:

    Instance identity is not represented merely by the object
    signature. Ownership multiplicity is explicitly encoded.

    This makes:

        I0 -> O0
        I1 -> O1

    structurally different from:

        I0 -> O1
        I1 -> O1
    """

    owner = world.objects[instance.object_id]

    return (
        "INSTANCE_OWNERSHIP",
        VERSION,
        ("owner_object_type", owner.object_type),
        (
            "owner_object_signature",
            owner.signature(world.units),
        ),
        (
            "owner_object_id_role",
            instance.object_id,
        ),
    )


def instance_multiset_signature(world: World) -> Tuple:
    """
    The raw object ID cannot be used directly for relabeling-invariant
    comparison.

    Therefore the representation contains two complementary pieces:

      1. object structural signature
      2. occupancy / ownership multiplicity

    For each structural object class, count how many instances own it.
    """

    object_classes: Dict[Any, List[int]] = {}

    for oid, obj in world.objects.items():
        sig = obj.signature(world.units)
        object_classes.setdefault(sig, []).append(oid)

    occupancy = []

    for obj_sig, object_ids in object_classes.items():
        counts = []
        for oid in object_ids:
            count = sum(
                1
                for inst in world.instances.values()
                if inst.object_id == oid
            )
            counts.append(count)

        occupancy.append(
            (
                "OBJECT_OCCUPANCY",
                obj_sig,
                tuple(sorted(counts)),
            )
        )

    return tuple(
        sorted(occupancy, key=repr)
    )


def relation_multiset_signature(world: World) -> Tuple:
    return tuple(
        sorted(
            (
                rel.signature(
                    world.objects,
                    world.units,
                )
                for rel in world.relations.values()
            ),
            key=repr,
        )
    )


# ============================================================
# v3.8 structural signature
# ============================================================

def structural_signature(world: World) -> Tuple:
    """
    v3.8 structural signature.

    It intentionally remains a structural-distance representation,
    not the v4.0 feature representation.

    Components:

        units
        objects
        instance ownership / occupancy
        relations
    """

    validate_world(world)

    return (
        "STRUCTURAL_DISTANCE_SIGNATURE",
        VERSION,

        (
            "UNITS",
            unit_multiset_signature(world),
        ),

        (
            "OBJECTS",
            object_multiset_signature(world),
        ),

        (
            "INSTANCES",
            instance_multiset_signature(world),
        ),

        (
            "RELATIONS",
            relation_multiset_signature(world),
        ),
    )


# ============================================================
# Canonical structural hash
# ============================================================

def structural_hash(world: World) -> str:
    return stable_hash(structural_signature(world))


# ============================================================
# Structural feature extraction
# ============================================================

def primitive_histogram(world: World) -> Dict[str, float]:
    result: Dict[str, float] = {}

    for unit in world.units.values():
        result[unit.primitive] = (
            result.get(unit.primitive, 0.0) + 1.0
        )

    return result


def object_count_histogram(world: World) -> Dict[str, float]:
    result: Dict[str, float] = {}

    for obj in world.objects.values():
        key = obj.object_type
        result[key] = result.get(key, 0.0) + 1.0

    return result


def object_composition_histogram(
    world: World,
) -> Dict[str, float]:
    """
    Counts primitive composition per object class.
    """

    result: Dict[str, float] = {}

    for obj in world.objects.values():
        primitives = sorted(
            world.units[uid].primitive
            for uid in obj.units
        )

        key = (
            obj.object_type,
            tuple(primitives),
        )

        result[repr(key)] = (
            result.get(repr(key), 0.0) + 1.0
        )

    return result


def instance_ownership_histogram(
    world: World,
) -> Dict[str, float]:
    """
    Explicit instance -> object ownership statistics.

    This is the critical v3.8 component.

    Example:

        Base:
            O0: 1 instance
            O1: 1 instance

        Mutation:
            O0: 0 instances
            O1: 2 instances

    gives different features.
    """

    result: Dict[str, float] = {}

    for oid, obj in world.objects.items():

        primitives = tuple(
            sorted(
                world.units[uid].primitive
                for uid in obj.units
            )
        )

        ownership_count = sum(
            1
            for inst in world.instances.values()
            if inst.object_id == oid
        )

        key = (
            obj.object_type,
            primitives,
            ownership_count,
        )

        result[repr(key)] = (
            result.get(repr(key), 0.0) + 1.0
        )

    return result


def relation_type_histogram(
    world: World,
) -> Dict[str, float]:
    result: Dict[str, float] = {}

    for rel in world.relations.values():
        result[rel.relation_type] = (
            result.get(rel.relation_type, 0.0) + 1.0
        )

    return result


def relation_confidence_statistics(
    world: World,
) -> Tuple[float, float, float, float]:
    values = [
        float(rel.confidence)
        for rel in world.relations.values()
    ]

    if not values:
        return (0.0, 0.0, 0.0, 0.0)

    mean = sum(values) / len(values)

    variance = sum(
        (x - mean) ** 2
        for x in values
    ) / len(values)

    return (
        float(len(values)),
        q(mean),
        q(min(values)),
        q(max(values)),
    )


# ============================================================
# Feature vector
# ============================================================

def numeric_feature_vector(world: World) -> Tuple[float, ...]:
    """
    Deterministic structural vector used ONLY by v3.8 distance.

    All categorical structural information is converted into
    deterministic histogram coordinates.
    """

    primitive_hist = primitive_histogram(world)
    object_hist = object_count_histogram(world)
    composition_hist = object_composition_histogram(world)
    ownership_hist = instance_ownership_histogram(world)
    relation_hist = relation_type_histogram(world)

    keys = set()

    for d in (
        primitive_hist,
        object_hist,
        composition_hist,
        ownership_hist,
        relation_hist,
    ):
        keys.update(d.keys())

    vector: List[float] = []

    # --------------------------------------------------------
    # Primitive structure
    # --------------------------------------------------------

    for key in sorted(primitive_hist):
        vector.append(
            primitive_hist[key]
        )

    # --------------------------------------------------------
    # Object counts
    # --------------------------------------------------------

    for key in sorted(object_hist):
        vector.append(
            object_hist[key]
        )

    # --------------------------------------------------------
    # Object composition
    # --------------------------------------------------------

    for key in sorted(composition_hist):
        vector.append(
            composition_hist[key]
        )

    # --------------------------------------------------------
    # Instance ownership
    # --------------------------------------------------------

    for key in sorted(ownership_hist):
        vector.append(
            ownership_hist[key]
        )

    # --------------------------------------------------------
    # Relation type
    # --------------------------------------------------------

    for key in sorted(relation_hist):
        vector.append(
            relation_hist[key]
        )

    # --------------------------------------------------------
    # Relation confidence
    # --------------------------------------------------------

    n_rel, mean_conf, min_conf, max_conf = (
        relation_confidence_statistics(world)
    )

    vector.extend([
        n_rel,
        mean_conf,
        min_conf,
        max_conf,
    ])

    return tuple(
        q(x)
        for x in vector
    )


# ============================================================
# Dimension alignment
# ============================================================

def feature_vector_aligned(
    a: World,
    b: World,
) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """
    Align sparse structural features by semantic key rather than
    relying on vector position.

    This is necessary because structural mutation may introduce
    a previously absent category.
    """

    def sparse_features(
        world: World,
    ) -> Dict[str, float]:

        result: Dict[str, float] = {}

        def add(prefix: str, data: Dict[str, float]):
            for k, v in data.items():
                result[f"{prefix}|{k}"] = float(v)

        add(
            "primitive",
            primitive_histogram(world),
        )

        add(
            "object",
            object_count_histogram(world),
        )

        add(
            "composition",
            object_composition_histogram(world),
        )

        add(
            "ownership",
            instance_ownership_histogram(world),
        )

        add(
            "relation_type",
            relation_type_histogram(world),
        )

        n, mean, mn, mx = relation_confidence_statistics(
            world
        )

        result["relation_count"] = n
        result["relation_confidence_mean"] = mean
        result["relation_confidence_min"] = mn
        result["relation_confidence_max"] = mx

        return result

    fa = sparse_features(a)
    fb = sparse_features(b)

    keys = sorted(
        set(fa.keys()) | set(fb.keys())
    )

    va = tuple(
        q(fa.get(k, 0.0))
        for k in keys
    )

    vb = tuple(
        q(fb.get(k, 0.0))
        for k in keys
    )

    return va, vb


# ============================================================
# Structural distance
# ============================================================

def structural_distance(
    a: World,
    b: World,
) -> float:
    """
    v3.8 structural distance.

        D(A,B) = ||F(A)-F(B)||_2

    The feature space is sparse and aligned by structural category.
    """

    va, vb = feature_vector_aligned(a, b)

    if len(va) != len(vb):
        raise AssertionError(
            "Aligned feature vectors must have equal dimension."
        )

    return q(
        math.sqrt(
            sum(
                (x - y) ** 2
                for x, y in zip(va, vb)
            )
        )
    )


# ============================================================
# Rigid transformation
# ============================================================

def rotate_z(
    point: Sequence[float],
    angle_degrees: float,
) -> Tuple[float, float, float]:

    theta = math.radians(angle_degrees)

    c = math.cos(theta)
    s = math.sin(theta)

    x, y, z = point

    return (
        q(c * x - s * y),
        q(s * x + c * y),
        q(z),
    )


def rigid_transform_world(
    world: World,
    angle_degrees: float = 90.0,
    translation: Tuple[float, float, float] = (
        17.25,
        -31.75,
        42.5,
    ),
) -> World:

    result = world.clone()

    for unit in result.units.values():

        transformed = []

        for p in unit.points:

            r = rotate_z(
                p,
                angle_degrees,
            )

            transformed.append(
                (
                    q(r[0] + translation[0]),
                    q(r[1] + translation[1]),
                    q(r[2] + translation[2]),
                )
            )

        unit.points = tuple(transformed)

    return result


# ============================================================
# Relabeling
# ============================================================

def permute_units(
    world: World,
    permutation: Sequence[int],
) -> World:

    result = world.clone()

    old_units = result.units

    mapping = {
        old_id: permutation[old_id]
        for old_id in old_units
    }

    new_units = {}

    for old_id, unit in old_units.items():

        new_id = mapping[old_id]

        copied = copy.deepcopy(unit)
        copied.uid = new_id

        new_units[new_id] = copied

    for obj in result.objects.values():
        obj.units = tuple(
            mapping[u]
            for u in obj.units
        )

    result.units = new_units

    return result


def permute_objects(
    world: World,
    permutation: Sequence[int],
) -> World:

    result = world.clone()

    mapping = {
        old_id: permutation[old_id]
        for old_id in result.objects
    }

    old_objects = result.objects
    new_objects = {}

    for old_id, obj in old_objects.items():

        copied = copy.deepcopy(obj)
        copied.oid = mapping[old_id]

        new_objects[copied.oid] = copied

    for inst in result.instances.values():
        inst.object_id = mapping[
            inst.object_id
        ]

    for rel in result.relations.values():
        rel.source_object = mapping[
            rel.source_object
        ]
        rel.target_object = mapping[
            rel.target_object
        ]

    result.objects = new_objects

    return result


def permute_instances(
    world: World,
    permutation: Sequence[int],
) -> World:

    result = world.clone()

    mapping = {
        old_id: permutation[old_id]
        for old_id in result.instances
    }

    old_instances = result.instances
    new_instances = {}

    for old_id, inst in old_instances.items():

        copied = copy.deepcopy(inst)
        copied.iid = mapping[old_id]

        new_instances[copied.iid] = copied

    result.instances = new_instances

    return result


def permute_relations(
    world: World,
    permutation: Sequence[int],
) -> World:

    result = world.clone()

    mapping = {
        old_id: permutation[old_id]
        for old_id in result.relations
    }

    old_relations = result.relations
    new_relations = {}

    for old_id, rel in old_relations.items():

        copied = copy.deepcopy(rel)
        copied.rid = mapping[old_id]

        new_relations[copied.rid] = copied

    result.relations = new_relations

    return result


# ============================================================
# Mutations
# ============================================================

def mutate_primitive(
    world: World,
) -> World:

    result = world.clone()

    result.units[0].primitive = (
        "cylinder"
    )

    return result


def mutate_object_composition(
    world: World,
) -> World:

    result = world.clone()

    # Base:
    #
    # O0 -> (0,3)
    # O1 -> (1,2)
    #
    # Mutation:
    #
    # O0 -> (0)
    # O1 -> (1,2,3)

    result.objects[0].units = (0,)
    result.objects[1].units = (1, 2, 3)

    return result


def mutate_instance_composition(
    world: World,
) -> World:

    result = world.clone()

    # Base:
    #
    # I0 -> O0
    # I1 -> O1
    #
    # Mutation:
    #
    # I0 -> O1
    # I1 -> O1

    result.instances[0].object_id = 1
    result.instances[1].object_id = 1

    return result


def mutate_relation_type(
    world: World,
) -> World:

    result = world.clone()

    result.relations[0].relation_type = (
        "contains"
    )

    return result


def mutate_relation_confidence(
    world: World,
) -> World:

    result = world.clone()

    result.relations[0].confidence = 0.10

    return result


def mutate_relation_deletion(
    world: World,
) -> World:

    result = world.clone()

    del result.relations[
        max(result.relations.keys())
    ]

    return result


# ============================================================
# Automorphism enumeration
# ============================================================

def automorphism_permutations(
    world: World,
) -> Iterable[Tuple[
    Sequence[int],
    Sequence[int],
    Sequence[int],
    Sequence[int],
]]:

    unit_ids = sorted(world.units.keys())
    object_ids = sorted(world.objects.keys())
    instance_ids = sorted(world.instances.keys())
    relation_ids = sorted(world.relations.keys())

    unit_perms = list(
        itertools.permutations(unit_ids)
    )

    object_perms = list(
        itertools.permutations(object_ids)
    )

    instance_perms = list(
        itertools.permutations(instance_ids)
    )

    relation_perms = list(
        itertools.permutations(relation_ids)
    )

    for up in unit_perms:
        for op in object_perms:
            for ip in instance_perms:
                for rp in relation_perms:

                    yield (
                        up,
                        op,
                        ip,
                        rp,
                    )


def apply_combined_permutation(
    world: World,
    unit_perm: Sequence[int],
    object_perm: Sequence[int],
    instance_perm: Sequence[int],
    relation_perm: Sequence[int],
) -> World:

    result = permute_units(
        world,
        unit_perm,
    )

    result = permute_objects(
        result,
        object_perm,
    )

    result = permute_instances(
        result,
        instance_perm,
    )

    result = permute_relations(
        result,
        relation_perm,
    )

    return result


# ============================================================
# Test framework
# ============================================================

class Regression:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed: List[str] = []

    def check(
        self,
        name: str,
        condition: bool,
    ) -> None:

        self.total += 1

        if condition:
            self.passed += 1
            print(
                f"[PASS] {name}"
            )
        else:
            self.failed.append(name)
            print(
                f"[FAIL] {name}"
            )


def section(title: str) -> None:
    print()
    print("-" * 60)
    print(title)
    print("-" * 60)


# ============================================================
# Main regression suite
# ============================================================

def main() -> None:

    print("=" * 60)
    print("Struct3D v3.8 Structural Distance Regression Suite")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Seed: {SEED}")

    reg = Regression()

    # --------------------------------------------------------
    # Base World
    # --------------------------------------------------------

    world = make_base_world()

    section("[1] Base World")

    print(
        f"Units: {len(world.units)}"
    )
    print(
        f"Objects: {len(world.objects)}"
    )
    print(
        f"Instances: {len(world.instances)}"
    )
    print(
        f"Relations: {len(world.relations)}"
    )

    try:
        validate_world(world)
        reg.check(
            "World Validation",
            True,
        )
    except Exception as exc:
        print(exc)
        reg.check(
            "World Validation",
            False,
        )

    # --------------------------------------------------------
    # Structural Distance
    # --------------------------------------------------------

    section("Structural Distance")

    d_ww = structural_distance(
        world,
        world,
    )

    print(
        f"D(W, W): {d_ww:.12f}"
    )

    reg.check(
        "Distance Exists",
        math.isfinite(d_ww),
    )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    section("Distance Identity")

    print(
        f"D(W, W): {d_ww:.12f}"
    )

    reg.check(
        "Identity",
        abs(d_ww) < EPS,
    )

    # --------------------------------------------------------
    # Symmetry
    # --------------------------------------------------------

    section("Distance Symmetry")

    mutation = mutate_primitive(world)

    d_wm = structural_distance(
        world,
        mutation,
    )

    d_mw = structural_distance(
        mutation,
        world,
    )

    print(
        f"D(W, M): {d_wm:.12f}"
    )
    print(
        f"D(M, W): {d_mw:.12f}"
    )

    reg.check(
        "Symmetry",
        abs(d_wm - d_mw) < EPS,
    )

    # --------------------------------------------------------
    # Dictionary Order
    # --------------------------------------------------------

    section("Dictionary Order Invariance")

    reordered = world.clone()

    reordered.units = dict(
        reversed(
            list(
                reordered.units.items()
            )
        )
    )

    reordered.objects = dict(
        reversed(
            list(
                reordered.objects.items()
            )
        )
    )

    reordered.instances = dict(
        reversed(
            list(
                reordered.instances.items()
            )
        )
    )

    reordered.relations = dict(
        reversed(
            list(
                reordered.relations.items()
            )
        )
    )

    d_reordered = structural_distance(
        world,
        reordered,
    )

    print(
        f"D(W, reordered(W)): "
        f"{d_reordered:.12f}"
    )

    reg.check(
        "Dictionary Order Invariance",
        abs(d_reordered) < EPS,
    )

    # --------------------------------------------------------
    # Unit relabeling
    # --------------------------------------------------------

    section("Unit Relabeling Invariance")

    unit_perm = [1, 0, 3, 2]

    unit_relabel = permute_units(
        world,
        unit_perm,
    )

    d_unit = structural_distance(
        world,
        unit_relabel,
    )

    print(
        f"Unit permutation: {unit_perm}"
    )
    print(
        f"D(W, pi_units(W)): "
        f"{d_unit:.12f}"
    )

    reg.check(
        "Unit Relabeling Invariance",
        abs(d_unit) < EPS,
    )

    # --------------------------------------------------------
    # Object relabeling
    # --------------------------------------------------------

    section("Object Relabeling Invariance")

    object_perm = [1, 0]

    object_relabel = permute_objects(
        world,
        object_perm,
    )

    d_object = structural_distance(
        world,
        object_relabel,
    )

    print(
        f"Object permutation: {object_perm}"
    )
    print(
        f"D(W, pi_objects(W)): "
        f"{d_object:.12f}"
    )

    reg.check(
        "Object Relabeling Invariance",
        abs(d_object) < EPS,
    )

    # --------------------------------------------------------
    # Instance relabeling
    # --------------------------------------------------------

    section("Instance Relabeling Invariance")

    instance_perm = [1, 0]

    instance_relabel = permute_instances(
        world,
        instance_perm,
    )

    d_instance = structural_distance(
        world,
        instance_relabel,
    )

    print(
        f"Instance permutation: "
        f"{instance_perm}"
    )
    print(
        f"D(W, pi_instances(W)): "
        f"{d_instance:.12f}"
    )

    reg.check(
        "Instance Relabeling Invariance",
        abs(d_instance) < EPS,
    )

    # --------------------------------------------------------
    # Relation relabeling
    # --------------------------------------------------------

    section("Relation Relabeling Invariance")

    relation_perm = [1, 0]

    relation_relabel = permute_relations(
        world,
        relation_perm,
    )

    d_relation = structural_distance(
        world,
        relation_relabel,
    )

    print(
        f"Relation permutation: "
        f"{relation_perm}"
    )
    print(
        f"D(W, pi_relations(W)): "
        f"{d_relation:.12f}"
    )

    reg.check(
        "Relation Relabeling Invariance",
        abs(d_relation) < EPS,
    )

    # --------------------------------------------------------
    # Combined relabeling
    # --------------------------------------------------------

    section("Combined Relabeling Invariance")

    combined = apply_combined_permutation(
        world,
        unit_perm,
        object_perm,
        instance_perm,
        relation_perm,
    )

    d_combined = structural_distance(
        world,
        combined,
    )

    print(
        f"D(W, pi_combined(W)): "
        f"{d_combined:.12f}"
    )

    reg.check(
        "Combined Relabeling Invariance",
        abs(d_combined) < EPS,
    )

    # --------------------------------------------------------
    # Rigid transform
    # --------------------------------------------------------

    section("Rigid Transform Invariance")

    transformed = rigid_transform_world(
        world,
        angle_degrees=90.0,
        translation=(
            17.25,
            -31.75,
            42.5,
        ),
    )

    d_transform = structural_distance(
        world,
        transformed,
    )

    print(
        "Rotation: Rz(90 deg)"
    )
    print(
        "Translation: "
        "(17.25, -31.75, 42.5)"
    )
    print(
        f"D(W, T(W)): "
        f"{d_transform:.12f}"
    )

    reg.check(
        "Rigid Transform Invariance",
        abs(d_transform) < EPS,
    )

    # --------------------------------------------------------
    # Automorphisms
    # --------------------------------------------------------

    section("Automorphism Compatibility")

    automorphism_count = 0

    base_hash = structural_hash(world)

    for (
        up,
        op,
        ip,
        rp,
    ) in automorphism_permutations(world):

        candidate = apply_combined_permutation(
            world,
            up,
            op,
            ip,
            rp,
        )

        if structural_hash(candidate) == base_hash:
            d = structural_distance(
                world,
                candidate,
            )

            if abs(d) >= EPS:
                raise AssertionError(
                    "Automorphism has non-zero distance."
                )

            automorphism_count += 1

    print(
        f"Automorphisms tested: "
        f"{automorphism_count}"
    )

    reg.check(
        "All Automorphisms Have Zero Distance",
        automorphism_count > 0,
    )

    # --------------------------------------------------------
    # Primitive mutation
    # --------------------------------------------------------

    section(
        "Structural Non-Equivalence: Primitive"
    )

    primitive_mutation = mutate_primitive(
        world
    )

    d_primitive = structural_distance(
        world,
        primitive_mutation,
    )

    print(
        f"D(W, primitive_mutation(W)): "
        f"{d_primitive:.12f}"
    )

    reg.check(
        "Primitive Mutation Has Positive Distance",
        d_primitive > EPS,
    )

    # --------------------------------------------------------
    # Object composition mutation
    # --------------------------------------------------------

    section(
        "Structural Non-Equivalence: "
        "Object Composition"
    )

    object_mutation = mutate_object_composition(
        world
    )

    print("Base object composition:")

    for oid in sorted(world.objects):
        print(
            f"  O{oid} -> "
            f"{world.objects[oid].units}"
        )

    print("Mutated object composition:")

    for oid in sorted(object_mutation.objects):
        print(
            f"  O{oid} -> "
            f"{object_mutation.objects[oid].units}"
        )

    d_object_mutation = structural_distance(
        world,
        object_mutation,
    )

    print(
        f"D(W, object_mutation(W)): "
        f"{d_object_mutation:.12f}"
    )

    reg.check(
        "Object Composition Mutation "
        "Has Positive Distance",
        d_object_mutation > EPS,
    )

    # --------------------------------------------------------
    # Instance composition mutation
    # --------------------------------------------------------

    section(
        "Structural Non-Equivalence: "
        "Instance Composition"
    )

    instance_mutation = mutate_instance_composition(
        world
    )

    print("Base instance composition:")

    for iid in sorted(world.instances):
        print(
            f"  I{iid} -> "
            f"O{world.instances[iid].object_id}"
        )

    print("Mutated instance composition:")

    for iid in sorted(instance_mutation.instances):
        print(
            f"  I{iid} -> "
            f"O{instance_mutation.instances[iid].object_id}"
        )

    d_instance_mutation = structural_distance(
        world,
        instance_mutation,
    )

    print(
        f"D(W, instance_mutation(W)): "
        f"{d_instance_mutation:.12f}"
    )

    reg.check(
        "Instance Composition Mutation "
        "Has Positive Distance",
        d_instance_mutation > EPS,
    )

    # --------------------------------------------------------
    # Relation type mutation
    # --------------------------------------------------------

    section(
        "Structural Non-Equivalence: "
        "Relation Type"
    )

    relation_type_mutation = mutate_relation_type(
        world
    )

    d_relation_type = structural_distance(
        world,
        relation_type_mutation,
    )

    print(
        f"D(W, relation_type_mutation(W)): "
        f"{d_relation_type:.12f}"
    )

    reg.check(
        "Relation Type Mutation "
        "Has Positive Distance",
        d_relation_type > EPS,
    )

    # --------------------------------------------------------
    # Relation confidence
    # --------------------------------------------------------

    section(
        "Structural Non-Equivalence: "
        "Relation Confidence"
    )

    confidence_mutation = (
        mutate_relation_confidence(world)
    )

    d_confidence = structural_distance(
        world,
        confidence_mutation,
    )

    print(
        f"D(W, confidence_mutation(W)): "
        f"{d_confidence:.12f}"
    )

    reg.check(
        "Relation Confidence Mutation "
        "Has Positive Distance",
        d_confidence > EPS,
    )

    # --------------------------------------------------------
    # Relation deletion
    # --------------------------------------------------------

    section(
        "Structural Non-Equivalence: "
        "Relation Deletion"
    )

    deletion_mutation = (
        mutate_relation_deletion(world)
    )

    d_deletion = structural_distance(
        world,
        deletion_mutation,
    )

    print(
        f"D(W, deletion_mutation(W)): "
        f"{d_deletion:.12f}"
    )

    reg.check(
        "Relation Deletion Has Positive Distance",
        d_deletion > EPS,
    )

    # --------------------------------------------------------
    # Triangle inequality
    # --------------------------------------------------------

    section("Triangle Inequality")

    A = world

    B = mutate_relation_confidence(
        world
    )

    C = mutate_primitive(
        world
    )

    d_ab = structural_distance(
        A,
        B,
    )

    d_bc = structural_distance(
        B,
        C,
    )

    d_ac = structural_distance(
        A,
        C,
    )

    print(
        f"D(A, B): {d_ab:.12f}"
    )
    print(
        f"D(B, C): {d_bc:.12f}"
    )
    print(
        f"D(A, C): {d_ac:.12f}"
    )
    print(
        f"D(A, B) + D(B, C): "
        f"{d_ab + d_bc:.12f}"
    )

    reg.check(
        "Triangle Inequality",
        d_ac <= d_ab + d_bc + EPS,
    )

    # --------------------------------------------------------
    # Repeated stability
    # --------------------------------------------------------

    section("Repeated Distance Stability")

    repeated_distances = []

    for _ in range(10):

        permuted = apply_combined_permutation(
            world,
            unit_perm,
            object_perm,
            instance_perm,
            relation_perm,
        )

        repeated_distances.append(
            structural_distance(
                world,
                permuted,
            )
        )

    print(
        f"Distances: "
        f"{repeated_distances}"
    )

    reg.check(
        "Repeated Relabeling Stability",
        all(
            abs(d) < EPS
            for d in repeated_distances
        ),
    )

    # --------------------------------------------------------
    # Structural mutation ordering
    # --------------------------------------------------------

    section("Structural Distance Ordering")

    mutation_distances = {
        "primitive": d_primitive,
        "object": d_object_mutation,
        "instance": d_instance_mutation,
        "relation_type": d_relation_type,
        "relation_confidence": d_confidence,
        "relation_deletion": d_deletion,
    }

    for name, value in mutation_distances.items():
        print(
            f"{name:<24}: "
            f"{value:.12f}"
        )

    positive = all(
        value > EPS
        for value in mutation_distances.values()
    )

    reg.check(
        "All Structural Mutations Are Separated",
        positive,
    )

    # --------------------------------------------------------
    # v3.8 Instance Composition Verification
    # --------------------------------------------------------

    section(
        "v3.8 Instance Composition Verification"
    )

    base_ownership = instance_ownership_histogram(
        world
    )

    mutated_ownership = instance_ownership_histogram(
        instance_mutation
    )

    print(
        "Base ownership:"
    )

    print(
        base_ownership
    )

    print(
        "Mutated ownership:"
    )

    print(
        mutated_ownership
    )

    ownership_changed = (
        base_ownership != mutated_ownership
    )

    print(
        f"Ownership changed: "
        f"{ownership_changed}"
    )

    reg.check(
        "Instance Ownership Enters "
        "Structural Signature",
        ownership_changed,
    )

    # --------------------------------------------------------
    # Hash mutation sensitivity
    # --------------------------------------------------------

    section(
        "Structural Hash Mutation Sensitivity"
    )

    base_structural_hash = structural_hash(
        world
    )

    instance_structural_hash = (
        structural_hash(
            instance_mutation
        )
    )

    print(
        "Base structural hash:"
    )
    print(
        base_structural_hash
    )

    print(
        "Instance mutation structural hash:"
    )
    print(
        instance_structural_hash
    )

    reg.check(
        "Structural Hash Changes Under "
        "Instance Mutation",
        base_structural_hash
        != instance_structural_hash,
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v3.8")
    print("=" * 60)

    print(
        f"Total tests: {reg.total}"
    )

    print(
        f"Passed: {reg.passed}"
    )

    print(
        f"Failed: {len(reg.failed)}"
    )

    if not reg.failed:
        print(
            "STATUS: PASS"
        )
    else:
        print(
            "STATUS: FAIL"
        )
        print()
        print("Failed tests:")

        for name in reg.failed:
            print(
                f"  - {name}"
            )

    print("=" * 60)

    if reg.failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()