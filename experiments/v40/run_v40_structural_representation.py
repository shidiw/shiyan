#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
Struct3D v4.0 — Structural Representation
============================================================

Version chain:

    v3.6  Structural Canonical Form
          |
    v3.7  Structural Invariant
          |
    v3.8  Structural Distance
          |
    v3.9  Structural Matching
          |
    v4.0  Structural Representation
          |
          v
    Neural Struct3D

============================================================

Core idea
============================================================

A structural world W is transformed into:

    W
      -> Canonical Representation C(W)
      -> Structural Invariant I(W)
      -> Structural Representation R(W)

The representation must satisfy:

1. Determinism
2. Dictionary-order invariance
3. Label permutation invariance
4. Rigid-transform invariance
5. Structural mutation sensitivity
6. Instance ownership sensitivity
7. Compatibility with v3.8 distance
8. Compatibility with v3.9 matching
9. Fixed dimensionality
10. Numerical stability
11. Serialization
12. Neural supervision compatibility

============================================================
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ============================================================
# Global Configuration
# ============================================================

VERSION = "4.0"
SEED = 20260814

random.seed(SEED)


# ============================================================
# Numeric Utilities
# ============================================================

EPS = 1e-12


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def safe_float(x: Any) -> float:
    return float(x)


def rounded_float(x: float, digits: int = 10) -> float:
    return round(float(x), digits)


def euclidean_distance(a: Sequence[float],
                       b: Sequence[float]) -> float:
    return math.sqrt(
        sum(
            (float(x) - float(y)) ** 2
            for x, y in zip(a, b)
        )
    )


def l2_distance(a: Sequence[float],
                b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError(
            f"Dimension mismatch: {len(a)} vs {len(b)}"
        )

    return math.sqrt(
        sum(
            (float(x) - float(y)) ** 2
            for x, y in zip(a, b)
        )
    )


# ============================================================
# Stable Serialization
# ============================================================

def stable_json(obj: Any) -> str:
    """
    Deterministic JSON serialization.

    Important:
    This function never relies on insertion order of dictionaries.
    """

    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def stable_hash(obj: Any) -> str:
    payload = stable_json(obj).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def freeze(obj: Any) -> Any:
    """
    Convert nested structures into deterministic tuples.
    """

    if isinstance(obj, dict):
        return tuple(
            sorted(
                (
                    str(k),
                    freeze(v)
                )
                for k, v in obj.items()
            )
        )

    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)

    if isinstance(obj, float):
        return rounded_float(obj)

    return obj


# ============================================================
# Geometry
# ============================================================

@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def as_tuple(self) -> Tuple[float, float, float]:
        return (
            float(self.x),
            float(self.y),
            float(self.z),
        )


def rotate_z(
    p: Sequence[float],
    angle_deg: float,
) -> Tuple[float, float, float]:

    theta = math.radians(angle_deg)

    c = math.cos(theta)
    s = math.sin(theta)

    x, y, z = p

    return (
        c * x - s * y,
        s * x + c * y,
        z,
    )


def rigid_transform(
    p: Sequence[float],
    angle_deg: float,
    translation: Sequence[float],
) -> Tuple[float, float, float]:

    r = rotate_z(p, angle_deg)

    return (
        r[0] + translation[0],
        r[1] + translation[1],
        r[2] + translation[2],
    )


# ============================================================
# Structural Entities
# ============================================================

@dataclass
class Unit:
    id: str
    primitive: str
    points: Tuple[Tuple[float, float, float], ...]
    scale: float = 1.0
    fit_error: float = 0.1

    def transformed(
        self,
        angle_deg: float,
        translation: Sequence[float],
    ) -> "Unit":

        pts = tuple(
            rigid_transform(
                p,
                angle_deg,
                translation,
            )
            for p in self.points
        )

        return Unit(
            id=self.id,
            primitive=self.primitive,
            points=pts,
            scale=self.scale,
            fit_error=self.fit_error,
        )


@dataclass
class ObjectNode:
    id: str
    object_type: str
    unit_ids: Tuple[str, ...]


@dataclass
class InstanceNode:
    id: str
    object_id: str
    instance_index: int = 0


@dataclass
class Relation:
    id: str
    source: str
    target: str
    relation_type: str
    confidence: float


@dataclass
class World:
    units: Dict[str, Unit]
    objects: Dict[str, ObjectNode]
    instances: Dict[str, InstanceNode]
    relations: Dict[str, Relation]


# ============================================================
# Primitive Signatures
# ============================================================

def unit_geometry_signature(unit: Unit) -> Tuple[Any, ...]:

    distances = []

    pts = unit.points

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            distances.append(
                rounded_float(
                    euclidean_distance(
                        pts[i],
                        pts[j],
                    )
                )
            )

    distances = tuple(sorted(distances))

    return (
        "UNIT",
        VERSION,
        unit.primitive,
        (
            "scale",
            rounded_float(unit.scale),
        ),
        (
            "fit",
            rounded_float(unit.fit_error),
        ),
        (
            "n",
            len(unit.points),
        ),
        (
            "dist",
            distances,
        ),
    )


def unit_signature(unit: Unit) -> Tuple[Any, ...]:
    return unit_geometry_signature(unit)


# ============================================================
# Object Signature
# ============================================================

def object_signature(
    world: World,
    obj: ObjectNode,
) -> Tuple[Any, ...]:

    unit_sigs = []

    for uid in obj.unit_ids:
        if uid not in world.units:
            raise KeyError(
                f"Object {obj.id} references missing unit {uid}"
            )

        unit_sigs.append(
            unit_signature(world.units[uid])
        )

    unit_sigs = tuple(
        sorted(
            unit_sigs,
            key=stable_json,
        )
    )

    return (
        "OBJECT",
        VERSION,
        obj.object_type,
        unit_sigs,
    )


# ============================================================
# Instance Ownership Signature
# ============================================================

def object_occupancy_signature(
    world: World,
    object_id: str,
) -> int:

    return sum(
        1
        for inst in world.instances.values()
        if inst.object_id == object_id
    )


def instance_signature(
    world: World,
    instance: InstanceNode,
) -> Tuple[Any, ...]:

    if instance.object_id not in world.objects:
        raise KeyError(
            f"Instance {instance.id} references "
            f"missing object {instance.object_id}"
        )

    obj = world.objects[instance.object_id]

    return (
        "INSTANCE",
        VERSION,
        object_signature(world, obj),
        (
            "instance_index",
            int(instance.instance_index),
        ),
    )


# ============================================================
# Relation Signature
# ============================================================

def relation_signature(
    relation: Relation,
) -> Tuple[Any, ...]:

    return (
        "RELATION",
        VERSION,
        relation.relation_type,
        rounded_float(relation.confidence),
        (
            "source_type",
            relation.source[0:1],
        ),
        (
            "target_type",
            relation.target[0:1],
        ),
    )


# ============================================================
# Structural Canonical Form
# ============================================================

def canonical_units(
    world: World,
) -> Tuple[Any, ...]:

    signatures = []

    for unit in world.units.values():
        signatures.append(
            unit_signature(unit)
        )

    return tuple(
        sorted(
            signatures,
            key=stable_json,
        )
    )


def canonical_objects(
    world: World,
) -> Tuple[Any, ...]:

    signatures = []

    for obj in world.objects.values():

        signatures.append(
            object_signature(
                world,
                obj,
            )
        )

    return tuple(
        sorted(
            signatures,
            key=stable_json,
        )
    )


def canonical_instances(
    world: World,
) -> Tuple[Any, ...]:

    signatures = []

    for inst in world.instances.values():

        obj_sig = object_signature(
            world,
            world.objects[inst.object_id],
        )

        occupancy = object_occupancy_signature(
            world,
            inst.object_id,
        )

        signatures.append(
            (
                "INSTANCE",
                VERSION,
                obj_sig,
                (
                    "occupancy",
                    occupancy,
                ),
            )
        )

    return tuple(
        sorted(
            signatures,
            key=stable_json,
        )
    )


def canonical_relations(
    world: World,
) -> Tuple[Any, ...]:

    signatures = []

    for rel in world.relations.values():

        signatures.append(
            relation_signature(rel)
        )

    return tuple(
        sorted(
            signatures,
            key=stable_json,
        )
    )


def canonical_structural_form(
    world: World,
) -> Tuple[Any, ...]:

    return (
        ("UNITS", canonical_units(world)),
        ("OBJECTS", canonical_objects(world)),
        ("INSTANCES", canonical_instances(world)),
        ("RELATIONS", canonical_relations(world)),
    )


# ============================================================
# Structural Invariant
# ============================================================

def structural_invariant(
    world: World,
) -> Tuple[Any, ...]:

    canonical = canonical_structural_form(world)

    return (
        ("STRUCT3D_INVARIANT", VERSION),
        canonical,
    )


def canonical_hash(world: World) -> str:
    return stable_hash(
        canonical_structural_form(world)
    )


def invariant_hash(world: World) -> str:
    return stable_hash(
        structural_invariant(world)
    )


# ============================================================
# Representation Components
# ============================================================

def primitive_histogram(
    world: World,
) -> Dict[str, int]:

    hist: Dict[str, int] = {}

    for unit in world.units.values():

        hist[unit.primitive] = (
            hist.get(unit.primitive, 0) + 1
        )

    return hist


def object_type_histogram(
    world: World,
) -> Dict[str, int]:

    hist: Dict[str, int] = {}

    for obj in world.objects.values():

        hist[obj.object_type] = (
            hist.get(obj.object_type, 0) + 1
        )

    return hist


def relation_type_histogram(
    world: World,
) -> Dict[str, int]:

    hist: Dict[str, int] = {}

    for rel in world.relations.values():

        hist[rel.relation_type] = (
            hist.get(rel.relation_type, 0) + 1
        )

    return hist


def relation_confidence_statistics(
    world: World,
) -> Tuple[float, float, float]:

    values = [
        float(r.confidence)
        for r in world.relations.values()
    ]

    if not values:
        return (
            0.0,
            0.0,
            0.0,
        )

    mean = sum(values) / len(values)

    variance = (
        sum(
            (x - mean) ** 2
            for x in values
        )
        / len(values)
    )

    return (
        mean,
        math.sqrt(variance),
        max(values),
    )


def object_size_statistics(
    world: World,
) -> Tuple[float, float, float]:

    sizes = [
        len(obj.unit_ids)
        for obj in world.objects.values()
    ]

    if not sizes:
        return (
            0.0,
            0.0,
            0.0,
        )

    return (
        sum(sizes) / len(sizes),
        min(sizes),
        max(sizes),
    )


def instance_occupancy_statistics(
    world: World,
) -> Tuple[float, float, float]:

    occupancies = [
        object_occupancy_signature(
            world,
            oid,
        )
        for oid in world.objects
    ]

    if not occupancies:
        return (
            0.0,
            0.0,
            0.0,
        )

    return (
        sum(occupancies) / len(occupancies),
        min(occupancies),
        max(occupancies),
    )


# ============================================================
# Fixed Primitive Vocabulary
# ============================================================

PRIMITIVE_VOCAB = (
    "plane",
    "sphere",
    "cylinder",
    "cone",
    "torus",
)

OBJECT_VOCAB = (
    "assembly",
    "component",
    "part",
    "structure",
)

RELATION_VOCAB = (
    "adjacent",
    "attached",
    "inside",
    "overlap",
    "supports",
)


def one_hot(
    value: str,
    vocabulary: Sequence[str],
) -> List[float]:

    return [
        1.0 if value == item else 0.0
        for item in vocabulary
    ]


# ============================================================
# Structural Representation
# ============================================================

def structural_representation(
    world: World,
) -> Tuple[float, ...]:

    """
    v4.0 fixed-dimensional representation.

    Dimensions:

        5 primitive histogram
        4 object histogram
        5 relation histogram
        3 relation confidence statistics
        3 object size statistics
        3 instance occupancy statistics

    Total:

        5 + 4 + 5 + 3 + 3 + 3 = 23

    """

    primitive_hist = primitive_histogram(world)

    object_hist = object_type_histogram(world)

    relation_hist = relation_type_histogram(world)

    representation: List[float] = []

    # --------------------------------------------------------
    # Primitive composition
    # --------------------------------------------------------

    unit_count = max(
        1,
        len(world.units),
    )

    for primitive in PRIMITIVE_VOCAB:

        count = primitive_hist.get(
            primitive,
            0,
        )

        representation.append(
            count / unit_count
        )

    # --------------------------------------------------------
    # Object composition
    # --------------------------------------------------------

    object_count = max(
        1,
        len(world.objects),
    )

    for object_type in OBJECT_VOCAB:

        count = object_hist.get(
            object_type,
            0,
        )

        representation.append(
            count / object_count
        )

    # --------------------------------------------------------
    # Relation composition
    # --------------------------------------------------------

    relation_count = max(
        1,
        len(world.relations),
    )

    for relation_type in RELATION_VOCAB:

        count = relation_hist.get(
            relation_type,
            0,
        )

        representation.append(
            count / relation_count
        )

    # --------------------------------------------------------
    # Relation confidence
    # --------------------------------------------------------

    mean_conf, std_conf, max_conf = (
        relation_confidence_statistics(world)
    )

    representation.extend(
        [
            mean_conf,
            std_conf,
            max_conf,
        ]
    )

    # --------------------------------------------------------
    # Object size
    # --------------------------------------------------------

    mean_size, min_size, max_size = (
        object_size_statistics(world)
    )

    representation.extend(
        [
            mean_size,
            min_size,
            max_size,
        ]
    )

    # --------------------------------------------------------
    # Instance occupancy
    # --------------------------------------------------------

    mean_occ, min_occ, max_occ = (
        instance_occupancy_statistics(world)
    )

    representation.extend(
        [
            mean_occ,
            min_occ,
            max_occ,
        ]
    )

    return tuple(
        rounded_float(x, 10)
        for x in representation
    )


# ============================================================
# Representation Metadata
# ============================================================

def representation_metadata(
    world: World,
) -> Dict[str, Any]:

    vector = structural_representation(world)

    return {
        "version": VERSION,
        "dimension": len(vector),
        "canonical_hash": canonical_hash(world),
        "invariant_hash": invariant_hash(world),
        "vector": vector,
    }


def representation_hash(
    world: World,
) -> str:

    return stable_hash(
        representation_metadata(world)
    )


# ============================================================
# Representation Distance
# ============================================================

def representation_distance(
    world_a: World,
    world_b: World,
) -> float:

    ra = structural_representation(world_a)
    rb = structural_representation(world_b)

    return l2_distance(
        ra,
        rb,
    )


# ============================================================
# Normalized Representation Distance
# ============================================================

def normalized_representation_distance(
    world_a: World,
    world_b: World,
) -> float:

    d = representation_distance(
        world_a,
        world_b,
    )

    return d / math.sqrt(
        max(
            1,
            len(
                structural_representation(world_a)
            ),
        )
    )


# ============================================================
# Neural Target
# ============================================================

def neural_struct3d_target(
    world: World,
) -> Dict[str, Any]:

    vector = structural_representation(world)

    return {
        "representation_version": VERSION,
        "representation": list(vector),
        "representation_dim": len(vector),
        "canonical_hash": canonical_hash(world),
        "invariant_hash": invariant_hash(world),
        "representation_hash": representation_hash(world),
    }


# ============================================================
# Base World
# ============================================================

def make_base_world() -> World:

    units = {
        "U0": Unit(
            id="U0",
            primitive="plane",
            points=(
                (0.0, 0.0, 0.0),
                (0.1, 0.0, 0.0),
                (0.0, 0.1, 0.0),
                (0.1, 0.1, 0.0),
            ),
        ),

        "U1": Unit(
            id="U1",
            primitive="sphere",
            points=(
                (1.0, 0.0, 0.0),
                (1.1, 0.0, 0.0),
                (1.0, 0.1, 0.0),
                (1.1, 0.1, 0.0),
            ),
        ),

        "U2": Unit(
            id="U2",
            primitive="plane",
            points=(
                (0.0, 1.0, 0.0),
                (0.1, 1.0, 0.0),
                (0.0, 1.1, 0.0),
                (0.1, 1.1, 0.0),
            ),
        ),

        "U3": Unit(
            id="U3",
            primitive="sphere",
            points=(
                (1.0, 1.0, 0.0),
                (1.1, 1.0, 0.0),
                (1.0, 1.1, 0.0),
                (1.1, 1.1, 0.0),
            ),
        ),
    }

    objects = {
        "O0": ObjectNode(
            id="O0",
            object_type="assembly",
            unit_ids=("U0", "U1"),
        ),

        "O1": ObjectNode(
            id="O1",
            object_type="assembly",
            unit_ids=("U2", "U3"),
        ),
    }

    instances = {
        "I0": InstanceNode(
            id="I0",
            object_id="O0",
            instance_index=0,
        ),

        "I1": InstanceNode(
            id="I1",
            object_id="O1",
            instance_index=1,
        ),
    }

    relations = {
        "R0": Relation(
            id="R0",
            source="O0",
            target="O1",
            relation_type="adjacent",
            confidence=0.9,
        ),

        "R1": Relation(
            id="R1",
            source="O1",
            target="O0",
            relation_type="attached",
            confidence=0.8,
        ),
    }

    return World(
        units=units,
        objects=objects,
        instances=instances,
        relations=relations,
    )


# ============================================================
# World Validation
# ============================================================

def validate_world(
    world: World,
) -> None:

    for obj in world.objects.values():

        for uid in obj.unit_ids:

            if uid not in world.units:
                raise AssertionError(
                    f"Missing unit: {uid}"
                )

    for inst in world.instances.values():

        if inst.object_id not in world.objects:
            raise AssertionError(
                f"Missing object: {inst.object_id}"
            )

    for rel in world.relations.values():

        if rel.source not in (
            set(world.objects)
            | set(world.instances)
            | set(world.units)
        ):
            raise AssertionError(
                f"Missing relation source: {rel.source}"
            )

        if rel.target not in (
            set(world.objects)
            | set(world.instances)
            | set(world.units)
        ):
            raise AssertionError(
                f"Missing relation target: {rel.target}"
            )


# ============================================================
# Dictionary Reordering
# ============================================================

def reorder_world(
    world: World,
) -> World:

    return World(
        units=dict(
            reversed(
                list(world.units.items())
            )
        ),
        objects=dict(
            reversed(
                list(world.objects.items())
            )
        ),
        instances=dict(
            reversed(
                list(world.instances.items())
            )
        ),
        relations=dict(
            reversed(
                list(world.relations.items())
            )
        ),
    )


# ============================================================
# Relabeling
# ============================================================

def relabel_units(
    world: World,
    permutation: Sequence[int],
) -> World:

    old_ids = list(world.units.keys())

    mapping = {
        old_ids[i]: f"U{permutation[i]}"
        for i in range(len(old_ids))
    }

    units = {}

    for old_id, unit in world.units.items():

        new_id = mapping[old_id]

        units[new_id] = Unit(
            id=new_id,
            primitive=unit.primitive,
            points=unit.points,
            scale=unit.scale,
            fit_error=unit.fit_error,
        )

    objects = {}

    for oid, obj in world.objects.items():

        objects[oid] = ObjectNode(
            id=oid,
            object_type=obj.object_type,
            unit_ids=tuple(
                mapping[u]
                for u in obj.unit_ids
            ),
        )

    return World(
        units=units,
        objects=objects,
        instances=copy.deepcopy(
            world.instances
        ),
        relations=copy.deepcopy(
            world.relations
        ),
    )


def relabel_objects(
    world: World,
    permutation: Sequence[int],
) -> World:

    old_ids = list(world.objects.keys())

    mapping = {
        old_ids[i]: f"O{permutation[i]}"
        for i in range(len(old_ids))
    }

    objects = {}

    for old_id, obj in world.objects.items():

        new_id = mapping[old_id]

        objects[new_id] = ObjectNode(
            id=new_id,
            object_type=obj.object_type,
            unit_ids=obj.unit_ids,
        )

    instances = {}

    for iid, inst in world.instances.items():

        instances[iid] = InstanceNode(
            id=iid,
            object_id=mapping[inst.object_id],
            instance_index=inst.instance_index,
        )

    relations = {}

    for rid, rel in world.relations.items():

        source = mapping.get(
            rel.source,
            rel.source,
        )

        target = mapping.get(
            rel.target,
            rel.target,
        )

        relations[rid] = Relation(
            id=rid,
            source=source,
            target=target,
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    return World(
        units=copy.deepcopy(world.units),
        objects=objects,
        instances=instances,
        relations=relations,
    )


def relabel_instances(
    world: World,
    permutation: Sequence[int],
) -> World:

    old_ids = list(world.instances.keys())

    mapping = {
        old_ids[i]: f"I{permutation[i]}"
        for i in range(len(old_ids))
    }

    instances = {}

    for old_id, inst in world.instances.items():

        new_id = mapping[old_id]

        instances[new_id] = InstanceNode(
            id=new_id,
            object_id=inst.object_id,
            instance_index=inst.instance_index,
        )

    relations = {}

    for rid, rel in world.relations.items():

        source = mapping.get(
            rel.source,
            rel.source,
        )

        target = mapping.get(
            rel.target,
            rel.target,
        )

        relations[rid] = Relation(
            id=rid,
            source=source,
            target=target,
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    return World(
        units=copy.deepcopy(world.units),
        objects=copy.deepcopy(world.objects),
        instances=instances,
        relations=relations,
    )


def relabel_relations(
    world: World,
    permutation: Sequence[int],
) -> World:

    old_ids = list(world.relations.keys())

    relations = {}

    for i, old_id in enumerate(old_ids):

        new_id = f"R{permutation[i]}"

        rel = world.relations[old_id]

        relations[new_id] = Relation(
            id=new_id,
            source=rel.source,
            target=rel.target,
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    return World(
        units=copy.deepcopy(world.units),
        objects=copy.deepcopy(world.objects),
        instances=copy.deepcopy(world.instances),
        relations=relations,
    )


# ============================================================
# Combined Relabeling
# ============================================================

def combined_relabeling(
    world: World,
) -> World:

    w = relabel_units(
        world,
        [1, 0, 3, 2],
    )

    w = relabel_objects(
        w,
        [1, 0],
    )

    w = relabel_instances(
        w,
        [1, 0],
    )

    w = relabel_relations(
        w,
        [1, 0],
    )

    return w


# ============================================================
# Rigid Transform
# ============================================================

def rigid_transform_world(
    world: World,
    angle_deg: float,
    translation: Sequence[float],
) -> World:

    units = {}

    for uid, unit in world.units.items():

        units[uid] = unit.transformed(
            angle_deg,
            translation,
        )

    return World(
        units=units,
        objects=copy.deepcopy(
            world.objects
        ),
        instances=copy.deepcopy(
            world.instances
        ),
        relations=copy.deepcopy(
            world.relations
        ),
    )


# ============================================================
# Structural Mutations
# ============================================================

def primitive_mutation(
    world: World,
) -> World:

    w = copy.deepcopy(world)

    w.units["U0"].primitive = "cylinder"

    return w


def object_mutation(
    world: World,
) -> World:

    w = copy.deepcopy(world)

    w.objects["O0"] = ObjectNode(
        id="O0",
        object_type="assembly",
        unit_ids=("U0",),
    )

    w.objects["O1"] = ObjectNode(
        id="O1",
        object_type="assembly",
        unit_ids=("U2", "U3", "U1"),
    )

    return w


def instance_mutation(
    world: World,
) -> World:

    w = copy.deepcopy(world)

    w.instances["I0"].object_id = "O1"

    return w


def relation_type_mutation(
    world: World,
) -> World:

    w = copy.deepcopy(world)

    w.relations["R0"].relation_type = "supports"

    return w


def confidence_mutation(
    world: World,
) -> World:

    w = copy.deepcopy(world)

    w.relations["R0"].confidence = 0.1

    return w


def relation_deletion_mutation(
    world: World,
) -> World:

    w = copy.deepcopy(world)

    del w.relations["R1"]

    return w


# ============================================================
# Assertion Utilities
# ============================================================

TOTAL_TESTS = 0
PASSED_TESTS = 0
FAILED_TESTS: List[str] = []


def check(
    name: str,
    condition: bool,
) -> bool:

    global TOTAL_TESTS
    global PASSED_TESTS

    TOTAL_TESTS += 1

    if condition:
        PASSED_TESTS += 1
        print(
            f"[PASS] {name}"
        )
        return True

    FAILED_TESTS.append(name)

    print(
        f"[FAIL] {name}"
    )

    return False


def section(
    title: str,
) -> None:

    print()
    print("-" * 60)
    print(title)
    print("-" * 60)


# ============================================================
# Main Regression Suite
# ============================================================

def main() -> None:

    global TOTAL_TESTS
    global PASSED_TESTS
    global FAILED_TESTS

    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = []

    print("=" * 60)
    print("Struct3D v4.0 Structural Representation Regression Suite")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Seed: {SEED}")

    # --------------------------------------------------------
    # Base World
    # --------------------------------------------------------

    section("[1] Base World")

    world = make_base_world()

    validate_world(world)

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

    check(
        "World Validation",
        True,
    )

    # --------------------------------------------------------
    # Canonical Form
    # --------------------------------------------------------

    section(
        "Canonical Structural Representation"
    )

    cform = canonical_structural_form(
        world
    )

    chash = canonical_hash(
        world
    )

    print(
        f"Canonical hash: {chash}"
    )

    check(
        "Canonical Form Exists",
        bool(cform)
        and len(chash) == 64,
    )

    # --------------------------------------------------------
    # Structural Invariant
    # --------------------------------------------------------

    section(
        "Structural Invariant"
    )

    ihash = invariant_hash(
        world
    )

    print(
        f"Invariant hash: {ihash}"
    )

    check(
        "Invariant Exists",
        bool(ihash)
        and len(ihash) == 64,
    )

    # --------------------------------------------------------
    # Representation
    # --------------------------------------------------------

    section(
        "Structural Representation"
    )

    rep = structural_representation(
        world
    )

    print(
        f"Feature count: {len(rep)}"
    )

    print(
        "Representation:"
    )
    print(
        json.dumps(
            list(rep),
            indent=2,
        )
    )

    print(
        f"Canonical hash: {chash}"
    )
    print(
        f"Invariant hash: {ihash}"
    )

    check(
        "Representation Exists",
        len(rep) == 23
        and all(
            math.isfinite(x)
            for x in rep
        ),
    )

    # --------------------------------------------------------
    # Representation Determinism
    # --------------------------------------------------------

    section(
        "Representation Determinism"
    )

    reps = [
        structural_representation(world)
        for _ in range(5)
    ]

    print(
        "Representations identical:",
        all(
            r == reps[0]
            for r in reps
        ),
    )

    check(
        "Representation Determinism",
        all(
            r == reps[0]
            for r in reps
        ),
    )

    # --------------------------------------------------------
    # Representation Hash
    # --------------------------------------------------------

    section(
        "Representation Hash"
    )

    rhash = representation_hash(
        world
    )

    print(
        f"Representation hash: {rhash}"
    )

    check(
        "Representation Hash Exists",
        len(rhash) == 64,
    )

    # --------------------------------------------------------
    # Dictionary Order Invariance
    # --------------------------------------------------------

    section(
        "Dictionary Order Invariance"
    )

    reordered = reorder_world(
        world
    )

    d_reordered = representation_distance(
        world,
        reordered,
    )

    print(
        f"R(W, reordered(W)): "
        f"{d_reordered:.12f}"
    )

    check(
        "Dictionary Order Invariance",
        abs(d_reordered) < EPS,
    )

    # --------------------------------------------------------
    # Unit Relabeling
    # --------------------------------------------------------

    section(
        "Unit Relabeling Invariance"
    )

    unit_perm = [1, 0, 3, 2]

    unit_relabel = relabel_units(
        world,
        unit_perm,
    )

    d_unit = representation_distance(
        world,
        unit_relabel,
    )

    print(
        f"Unit permutation: {unit_perm}"
    )

    print(
        f"R(W, pi_units(W)): "
        f"{d_unit:.12f}"
    )

    check(
        "Unit Relabeling Invariance",
        abs(d_unit) < EPS,
    )

    # --------------------------------------------------------
    # Object Relabeling
    # --------------------------------------------------------

    section(
        "Object Relabeling Invariance"
    )

    object_relabel = relabel_objects(
        world,
        [1, 0],
    )

    d_object = representation_distance(
        world,
        object_relabel,
    )

    print(
        f"Object permutation: [1, 0]"
    )

    print(
        f"R(W, pi_objects(W)): "
        f"{d_object:.12f}"
    )

    check(
        "Object Relabeling Invariance",
        abs(d_object) < EPS,
    )

    # --------------------------------------------------------
    # Instance Relabeling
    # --------------------------------------------------------

    section(
        "Instance Relabeling Invariance"
    )

    instance_relabel = relabel_instances(
        world,
        [1, 0],
    )

    d_instance = representation_distance(
        world,
        instance_relabel,
    )

    print(
        f"Instance permutation: [1, 0]"
    )

    print(
        f"R(W, pi_instances(W)): "
        f"{d_instance:.12f}"
    )

    check(
        "Instance Relabeling Invariance",
        abs(d_instance) < EPS,
    )

    # --------------------------------------------------------
    # Relation Relabeling
    # --------------------------------------------------------

    section(
        "Relation Relabeling Invariance"
    )

    relation_relabel = relabel_relations(
        world,
        [1, 0],
    )

    d_relation = representation_distance(
        world,
        relation_relabel,
    )

    print(
        f"Relation permutation: [1, 0]"
    )

    print(
        f"R(W, pi_relations(W)): "
        f"{d_relation:.12f}"
    )

    check(
        "Relation Relabeling Invariance",
        abs(d_relation) < EPS,
    )

    # --------------------------------------------------------
    # Combined Relabeling
    # --------------------------------------------------------

    section(
        "Combined Relabeling Invariance"
    )

    combined = combined_relabeling(
        world
    )

    d_combined = representation_distance(
        world,
        combined,
    )

    print(
        f"R(W, pi_combined(W)): "
        f"{d_combined:.12f}"
    )

    check(
        "Combined Relabeling Invariance",
        abs(d_combined) < EPS,
    )

    # --------------------------------------------------------
    # Rigid Transform
    # --------------------------------------------------------

    section(
        "Rigid Transform Invariance"
    )

    transformed = rigid_transform_world(
        world,
        90.0,
        (17.25, -31.75, 42.5),
    )

    d_transform = representation_distance(
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
        f"R(W, T(W)): "
        f"{d_transform:.12f}"
    )

    check(
        "Rigid Transform Invariance",
        abs(d_transform) < EPS,
    )

    # --------------------------------------------------------
    # Primitive Mutation
    # --------------------------------------------------------

    section(
        "Representation Mutation: Primitive"
    )

    primitive_world = primitive_mutation(
        world
    )

    primitive_distance = representation_distance(
        world,
        primitive_world,
    )

    print(
        f"R(W, primitive_mutation(W)): "
        f"{primitive_distance:.12f}"
    )

    check(
        "Primitive Mutation Has Positive Distance",
        primitive_distance > EPS,
    )

    # --------------------------------------------------------
    # Object Mutation
    # --------------------------------------------------------

    section(
        "Representation Mutation: Object Composition"
    )

    object_world = object_mutation(
        world
    )

    object_distance = representation_distance(
        world,
        object_world,
    )

    print(
        f"R(W, object_mutation(W)): "
        f"{object_distance:.12f}"
    )

    check(
        "Object Mutation Has Positive Distance",
        object_distance > EPS,
    )

    # --------------------------------------------------------
    # Instance Mutation
    # --------------------------------------------------------

    section(
        "Representation Mutation: Instance Composition"
    )

    instance_world = instance_mutation(
        world
    )

    instance_distance = representation_distance(
        world,
        instance_world,
    )

    print(
        f"R(W, instance_mutation(W)): "
        f"{instance_distance:.12f}"
    )

    check(
        "Instance Mutation Has Positive Distance",
        instance_distance > EPS,
    )

    # --------------------------------------------------------
    # Relation Type Mutation
    # --------------------------------------------------------

    section(
        "Representation Mutation: Relation Type"
    )

    relation_type_world = relation_type_mutation(
        world
    )

    relation_type_distance = (
        representation_distance(
            world,
            relation_type_world,
        )
    )

    print(
        f"R(W, relation_type_mutation(W)): "
        f"{relation_type_distance:.12f}"
    )

    check(
        "Relation Type Mutation Has Positive Distance",
        relation_type_distance > EPS,
    )

    # --------------------------------------------------------
    # Confidence Mutation
    # --------------------------------------------------------

    section(
        "Representation Mutation: Relation Confidence"
    )

    confidence_world = confidence_mutation(
        world
    )

    confidence_distance = (
        representation_distance(
            world,
            confidence_world,
        )
    )

    print(
        f"R(W, confidence_mutation(W)): "
        f"{confidence_distance:.12f}"
    )

    check(
        "Relation Confidence Mutation Has Positive Distance",
        confidence_distance > EPS,
    )

    # --------------------------------------------------------
    # Relation Deletion
    # --------------------------------------------------------

    section(
        "Representation Mutation: Relation Deletion"
    )

    deletion_world = relation_deletion_mutation(
        world
    )

    deletion_distance = (
        representation_distance(
            world,
            deletion_world,
        )
    )

    print(
        f"R(W, deletion_mutation(W)): "
        f"{deletion_distance:.12f}"
    )

    check(
        "Relation Deletion Has Positive Distance",
        deletion_distance > EPS,
    )

    # --------------------------------------------------------
    # Representation Ordering
    # --------------------------------------------------------

    section(
        "Structural Representation Ordering"
    )

    mutation_distances = {
        "primitive": primitive_distance,
        "object": object_distance,
        "instance": instance_distance,
        "relation_type": relation_type_distance,
        "relation_confidence": confidence_distance,
        "relation_deletion": deletion_distance,
    }

    for name, value in mutation_distances.items():

        print(
            f"{name:20s}: "
            f"{value:.12f}"
        )

    check(
        "All Structural Mutations Produce Positive Representation Distance",
        all(
            value > EPS
            for value in mutation_distances.values()
        ),
    )

    # --------------------------------------------------------
    # Instance Occupancy Verification
    # --------------------------------------------------------

    section(
        "v4.0 Instance Occupancy Verification"
    )

    base_occ = instance_occupancy_statistics(
        world
    )

    mutated_occ = instance_occupancy_statistics(
        instance_world
    )

    print(
        "Base occupancy statistics:"
    )
    print(
        base_occ
    )

    print(
        "Mutated occupancy statistics:"
    )
    print(
        mutated_occ
    )

    occupancy_changed = (
        base_occ != mutated_occ
    )

    print(
        f"Occupancy changed: "
        f"{occupancy_changed}"
    )

    check(
        "Instance Occupancy Enters Representation",
        occupancy_changed,
    )

    # --------------------------------------------------------
    # Canonical Hash Mutation
    # --------------------------------------------------------

    section(
        "Canonical Hash Mutation Sensitivity"
    )

    base_hash = canonical_hash(
        world
    )

    instance_hash = canonical_hash(
        instance_world
    )

    print(
        "Base canonical hash:"
    )
    print(base_hash)

    print(
        "Instance mutation canonical hash:"
    )
    print(instance_hash)

    check(
        "Canonical Hash Changes Under Instance Mutation",
        base_hash != instance_hash,
    )

    # --------------------------------------------------------
    # Representation Hash Mutation
    # --------------------------------------------------------

    section(
        "Representation Hash Mutation Sensitivity"
    )

    base_rep_hash = representation_hash(
        world
    )

    mutated_rep_hash = representation_hash(
        instance_world
    )

    print(
        "Base representation hash:"
    )
    print(base_rep_hash)

    print(
        "Instance mutation representation hash:"
    )
    print(mutated_rep_hash)

    check(
        "Representation Hash Changes Under Instance Mutation",
        base_rep_hash != mutated_rep_hash,
    )

    # --------------------------------------------------------
    # Neural Target
    # --------------------------------------------------------

    section(
        "Neural Struct3D Compatibility"
    )

    neural_target = neural_struct3d_target(
        world
    )

    print(
        json.dumps(
            neural_target,
            indent=2,
            sort_keys=True,
        )
    )

    serialized = stable_json(
        neural_target
    )

    try:

        decoded = json.loads(
            serialized
        )

        neural_serializable = (
            decoded["representation_dim"]
            == len(rep)
            and len(
                decoded["representation"]
            ) == len(rep)
        )

    except Exception:

        neural_serializable = False

    check(
        "Neural Representation Target Is Serializable",
        neural_serializable,
    )

    # --------------------------------------------------------
    # Representation Distance Consistency
    # --------------------------------------------------------

    section(
        "Representation Distance Consistency"
    )

    d_forward = representation_distance(
        world,
        instance_world,
    )

    d_backward = representation_distance(
        instance_world,
        world,
    )

    print(
        f"R(W, I_mut): "
        f"{d_forward:.12f}"
    )

    print(
        f"R(I_mut, W): "
        f"{d_backward:.12f}"
    )

    check(
        "Representation Distance Symmetry",
        abs(
            d_forward - d_backward
        ) < EPS,
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v4.0")
    print("=" * 60)

    print(
        f"Total tests: {TOTAL_TESTS}"
    )

    print(
        f"Passed: {PASSED_TESTS}"
    )

    print(
        f"Failed: {len(FAILED_TESTS)}"
    )

    if FAILED_TESTS:

        print(
            "STATUS: FAIL"
        )

        print()

        print(
            "Failed tests:"
        )

        for name in FAILED_TESTS:

            print(
                f"  - {name}"
            )

    else:

        print(
            "STATUS: PASS"
        )

    print(
        "=" * 60
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()