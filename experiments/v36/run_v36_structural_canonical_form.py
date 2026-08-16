#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Struct3D v3.6 Structural Canonical Form Regression Suite

Purpose
-------
v3.2 : Structural Equivalence
v3.3 : Structural Isomorphism
v3.4 : Structural Automorphism
v3.5 : Structural Quotient
v3.6 : Structural Canonical Form

Core statement
--------------
For structural worlds W1 and W2:

    W1 ≅ W2
        iff
    Canon(W1) == Canon(W2)

The canonical form removes arbitrary labels while preserving
all structural information relevant to Struct3D.

This file is intentionally self-contained.
No dependency on v3.2-v3.5 implementation files is required.

CPU-only.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


# ============================================================
# Configuration
# ============================================================

VERSION = "3.6"
SEED = 20260814

random.seed(SEED)


# ============================================================
# Utility
# ============================================================

def qfloat(x: float, digits: int = 10) -> float:
    return round(float(x), digits)


def freeze(value: Any) -> Any:
    """
    Convert nested Python objects into deterministic immutable tuples.
    """
    if isinstance(value, dict):
        return tuple(
            sorted(
                (
                    str(k),
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
        return qfloat(value)

    return value


def stable_hash(value: Any) -> str:
    payload = repr(freeze(value)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ============================================================
# Primitive
# ============================================================

@dataclass
class Primitive:
    kind: str
    params: Dict[str, Any] = field(default_factory=dict)

    def canonical(self) -> Tuple[Any, ...]:
        return (
            "PRIMITIVE",
            VERSION,
            self.kind,
            freeze(self.params),
        )


# ============================================================
# Unit
# ============================================================

@dataclass
class Unit:
    uid: int
    primitive: Primitive
    features: Dict[str, Any] = field(default_factory=dict)

    def structural_signature(self) -> Tuple[Any, ...]:
        return (
            "UNIT",
            VERSION,
            self.primitive.canonical(),
            freeze(self.features),
        )


# ============================================================
# Object
# ============================================================

@dataclass
class ObjectNode:
    oid: int
    object_type: str
    units: List[int]
    attributes: Dict[str, Any] = field(default_factory=dict)

    def local_signature(
        self,
        unit_signatures: Mapping[int, Tuple[Any, ...]],
    ) -> Tuple[Any, ...]:
        parts = tuple(
            sorted(
                unit_signatures[u]
                for u in self.units
            )
        )

        return (
            "OBJECT",
            VERSION,
            self.object_type,
            parts,
            freeze(self.attributes),
        )


# ============================================================
# Instance
# ============================================================

@dataclass
class InstanceNode:
    iid: int
    object_id: int
    attributes: Dict[str, Any] = field(default_factory=dict)

    def local_signature(
        self,
        object_signatures: Mapping[int, Tuple[Any, ...]],
    ) -> Tuple[Any, ...]:
        return (
            "INSTANCE",
            VERSION,
            object_signatures[self.object_id],
            freeze(self.attributes),
        )


# ============================================================
# Relation
# ============================================================

@dataclass
class Relation:
    rid: int
    source_instance: int
    target_instance: int
    relation_type: str
    confidence: float

    def local_signature(
        self,
        instance_signatures: Mapping[int, Tuple[Any, ...]],
    ) -> Tuple[Any, ...]:

        return (
            "RELATION",
            VERSION,
            instance_signatures[self.source_instance],
            instance_signatures[self.target_instance],
            freeze(
                {
                    "type": self.relation_type,
                    "confidence": qfloat(self.confidence),
                }
            ),
        )


# ============================================================
# World
# ============================================================

@dataclass
class World:
    units: Dict[int, Unit]
    objects: Dict[int, ObjectNode]
    instances: Dict[int, InstanceNode]
    relations: Dict[int, Relation]

    def copy(self) -> "World":
        return copy.deepcopy(self)

    def validate(self) -> bool:

        # Unit references
        for obj in self.objects.values():
            for uid in obj.units:
                if uid not in self.units:
                    return False

        # Object references
        for inst in self.instances.values():
            if inst.object_id not in self.objects:
                return False

        # Instance references
        for rel in self.relations.values():
            if rel.source_instance not in self.instances:
                return False
            if rel.target_instance not in self.instances:
                return False

        return True

    def statistics(self) -> Dict[str, int]:
        return {
            "units": len(self.units),
            "objects": len(self.objects),
            "instances": len(self.instances),
            "relations": len(self.relations),
        }


# ============================================================
# Structural Signatures
# ============================================================

def compute_unit_signatures(
    world: World,
) -> Dict[int, Tuple[Any, ...]]:

    return {
        uid: unit.structural_signature()
        for uid, unit in world.units.items()
    }


def compute_object_signatures(
    world: World,
    unit_signatures: Mapping[int, Tuple[Any, ...]],
) -> Dict[int, Tuple[Any, ...]]:

    return {
        oid: obj.local_signature(unit_signatures)
        for oid, obj in world.objects.items()
    }


def compute_instance_signatures(
    world: World,
    object_signatures: Mapping[int, Tuple[Any, ...]],
) -> Dict[int, Tuple[Any, ...]]:

    return {
        iid: inst.local_signature(object_signatures)
        for iid, inst in world.instances.items()
    }


def compute_relation_signatures(
    world: World,
    instance_signatures: Mapping[int, Tuple[Any, ...]],
) -> Dict[int, Tuple[Any, ...]]:

    return {
        rid: rel.local_signature(instance_signatures)
        for rid, rel in world.relations.items()
    }


# ============================================================
# Relabeling
# ============================================================

def invert_permutation(
    permutation: Sequence[int],
) -> Dict[int, int]:

    return {
        old: new
        for new, old in enumerate(permutation)
    }


def relabel_world(
    world: World,
    unit_perm: Sequence[int] | None = None,
    object_perm: Sequence[int] | None = None,
    instance_perm: Sequence[int] | None = None,
    relation_perm: Sequence[int] | None = None,
) -> World:

    result = world.copy()

    unit_ids = sorted(result.units)
    object_ids = sorted(result.objects)
    instance_ids = sorted(result.instances)
    relation_ids = sorted(result.relations)

    if unit_perm is None:
        unit_perm = list(range(len(unit_ids)))

    if object_perm is None:
        object_perm = list(range(len(object_ids)))

    if instance_perm is None:
        instance_perm = list(range(len(instance_ids)))

    if relation_perm is None:
        relation_perm = list(range(len(relation_ids)))

    unit_map = {
        unit_ids[i]: unit_perm[i]
        for i in range(len(unit_ids))
    }

    object_map = {
        object_ids[i]: object_perm[i]
        for i in range(len(object_ids))
    }

    instance_map = {
        instance_ids[i]: instance_perm[i]
        for i in range(len(instance_ids))
    }

    relation_map = {
        relation_ids[i]: relation_perm[i]
        for i in range(len(relation_ids))
    }

    new_units: Dict[int, Unit] = {}

    for old_id, unit in result.units.items():
        new_id = unit_map[old_id]

        new_units[new_id] = Unit(
            uid=new_id,
            primitive=copy.deepcopy(unit.primitive),
            features=copy.deepcopy(unit.features),
        )

    new_objects: Dict[int, ObjectNode] = {}

    for old_id, obj in result.objects.items():

        new_id = object_map[old_id]

        new_objects[new_id] = ObjectNode(
            oid=new_id,
            object_type=obj.object_type,
            units=[
                unit_map[u]
                for u in obj.units
            ],
            attributes=copy.deepcopy(obj.attributes),
        )

    new_instances: Dict[int, InstanceNode] = {}

    for old_id, inst in result.instances.items():

        new_id = instance_map[old_id]

        new_instances[new_id] = InstanceNode(
            iid=new_id,
            object_id=object_map[inst.object_id],
            attributes=copy.deepcopy(inst.attributes),
        )

    new_relations: Dict[int, Relation] = {}

    for old_id, rel in result.relations.items():

        new_id = relation_map[old_id]

        new_relations[new_id] = Relation(
            rid=new_id,
            source_instance=instance_map[rel.source_instance],
            target_instance=instance_map[rel.target_instance],
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    return World(
        units=new_units,
        objects=new_objects,
        instances=new_instances,
        relations=new_relations,
    )


# ============================================================
# Canonical Form
# ============================================================

def canonical_unit_record(
    unit: Unit,
) -> Tuple[Any, ...]:

    return (
        "UNIT",
        unit.primitive.canonical(),
        freeze(unit.features),
    )


def canonical_object_record(
    obj: ObjectNode,
    unit_records: Mapping[int, Tuple[Any, ...]],
) -> Tuple[Any, ...]:

    return (
        "OBJECT",
        obj.object_type,
        tuple(
            sorted(
                unit_records[u]
                for u in obj.units
            )
        ),
        freeze(obj.attributes),
    )


def canonical_instance_record(
    inst: InstanceNode,
    object_records: Mapping[int, Tuple[Any, ...]],
) -> Tuple[Any, ...]:

    return (
        "INSTANCE",
        object_records[inst.object_id],
        freeze(inst.attributes),
    )


def canonical_relation_record(
    rel: Relation,
    instance_records: Mapping[int, Tuple[Any, ...]],
) -> Tuple[Any, ...]:

    return (
        "RELATION",
        instance_records[rel.source_instance],
        instance_records[rel.target_instance],
        rel.relation_type,
        qfloat(rel.confidence),
    )


def structural_canonical_form(
    world: World,
) -> Tuple[Any, ...]:
    """
    Canonical structural representation.

    Important:
    The implementation recursively replaces arbitrary identifiers
    by structural records. Entity lists are sorted lexicographically.

    Thus dictionary insertion order and integer labels disappear.
    """

    if not world.validate():
        raise ValueError("Invalid world")

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    unit_records = {
        uid: canonical_unit_record(unit)
        for uid, unit in world.units.items()
    }

    canonical_units = tuple(
        sorted(unit_records.values())
    )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    object_records = {
        oid: canonical_object_record(
            obj,
            unit_records,
        )
        for oid, obj in world.objects.items()
    }

    canonical_objects = tuple(
        sorted(object_records.values())
    )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    instance_records = {
        iid: canonical_instance_record(
            inst,
            object_records,
        )
        for iid, inst in world.instances.items()
    }

    canonical_instances = tuple(
        sorted(instance_records.values())
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    relation_records = {
        rid: canonical_relation_record(
            rel,
            instance_records,
        )
        for rid, rel in world.relations.items()
    }

    canonical_relations = tuple(
        sorted(relation_records.values())
    )

    # --------------------------------------------------------
    # Final canonical world
    # --------------------------------------------------------

    return (
        "STRUCT3D_CANONICAL_FORM",
        VERSION,
        canonical_units,
        canonical_objects,
        canonical_instances,
        canonical_relations,
    )


def canonical_hash(
    world: World,
) -> str:

    return stable_hash(
        structural_canonical_form(world)
    )


# ============================================================
# Structural Quotient
# ============================================================

def structural_quotient(
    world: World,
) -> Tuple[Any, ...]:

    canonical = structural_canonical_form(world)

    units = canonical[2]
    objects = canonical[3]
    instances = canonical[4]
    relations = canonical[5]

    return (
        "STRUCTURAL_QUOTIENT",
        VERSION,
        len(units),
        len(objects),
        len(instances),
        len(relations),
        units,
        objects,
        instances,
        relations,
    )


def quotient_hash(
    world: World,
) -> str:

    return stable_hash(
        structural_quotient(world)
    )


# ============================================================
# Automorphism Enumeration
# ============================================================

def all_permutations(n: int) -> Iterable[Tuple[int, ...]]:
    return itertools.permutations(range(n))


def is_automorphism(
    world: World,
    unit_perm: Sequence[int],
    object_perm: Sequence[int],
    instance_perm: Sequence[int],
    relation_perm: Sequence[int],
) -> bool:

    transformed = relabel_world(
        world,
        unit_perm=unit_perm,
        object_perm=object_perm,
        instance_perm=instance_perm,
        relation_perm=relation_perm,
    )

    return (
        structural_canonical_form(world)
        ==
        structural_canonical_form(transformed)
    )


def enumerate_automorphisms(
    world: World,
    max_tests: int = 100000,
) -> List[Tuple[
    Tuple[int, ...],
    Tuple[int, ...],
    Tuple[int, ...],
    Tuple[int, ...],
]]:

    n_u = len(world.units)
    n_o = len(world.objects)
    n_i = len(world.instances)
    n_r = len(world.relations)

    result = []

    tested = 0

    for up in all_permutations(n_u):

        for op in all_permutations(n_o):

            for ip in all_permutations(n_i):

                for rp in all_permutations(n_r):

                    if tested >= max_tests:
                        return result

                    tested += 1

                    if is_automorphism(
                        world,
                        up,
                        op,
                        ip,
                        rp,
                    ):
                        result.append(
                            (
                                up,
                                op,
                                ip,
                                rp,
                            )
                        )

    return result


# ============================================================
# Base World
# ============================================================

def build_base_world() -> World:

    units = {
        0: Unit(
            0,
            Primitive(
                "plane",
                {
                    "scale": 1.0,
                    "fit": 0.1,
                },
            ),
        ),

        1: Unit(
            1,
            Primitive(
                "plane",
                {
                    "scale": 1.0,
                    "fit": 0.1,
                },
            ),
        ),

        2: Unit(
            2,
            Primitive(
                "sphere",
                {
                    "scale": 1.0,
                    "fit": 0.1,
                },
            ),
        ),

        3: Unit(
            3,
            Primitive(
                "sphere",
                {
                    "scale": 1.0,
                    "fit": 0.1,
                },
            ),
        ),
    }

    objects = {
        0: ObjectNode(
            oid=0,
            object_type="assembly",
            units=[0, 2],
        ),

        1: ObjectNode(
            oid=1,
            object_type="assembly",
            units=[1, 3],
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
            source_instance=0,
            target_instance=1,
            relation_type="adjacent",
            confidence=0.9,
        ),

        1: Relation(
            rid=1,
            source_instance=1,
            target_instance=0,
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
# Test Framework
# ============================================================

class RegressionSuite:

    def __init__(self):
        self.total = 0
        self.passed = 0

    def section(self, title: str):

        print()
        print("-" * 60)
        print(title)
        print("-" * 60)

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
            print(f"[FAIL] {name}")

    def summary(self):

        failed = self.total - self.passed

        print()
        print("=" * 60)
        print(f"Struct3D v{VERSION}")
        print("=" * 60)

        print(
            f"Total tests: {self.total}"
        )

        print(
            f"Passed: {self.passed}"
        )

        print(
            f"Failed: {failed}"
        )

        print(
            f"STATUS: {'PASS' if failed == 0 else 'FAIL'}"
        )

        print("=" * 60)


# ============================================================
# Main Regression Suite
# ============================================================

def main():

    suite = RegressionSuite()

    print("=" * 60)
    print(
        "Struct3D v3.6 Structural Canonical Form Regression Suite"
    )
    print("=" * 60)

    print(f"Version: {VERSION}")
    print(f"Seed: {SEED}")

    # ========================================================
    # 1. Base World
    # ========================================================

    suite.section("[1] Base World")

    world = build_base_world()

    stats = world.statistics()

    print(f"Units: {stats['units']}")
    print(f"Objects: {stats['objects']}")
    print(f"Instances: {stats['instances']}")
    print(f"Relations: {stats['relations']}")

    suite.check(
        "World Validation",
        world.validate()
        and stats == {
            "units": 4,
            "objects": 2,
            "instances": 2,
            "relations": 2,
        },
    )

    # ========================================================
    # 2. Canonical Form Exists
    # ========================================================

    suite.section("Canonical Form")

    canonical = structural_canonical_form(world)

    print(
        "Canonical form generated:",
        canonical is not None,
    )

    print(
        "Canonical hash:",
        canonical_hash(world),
    )

    suite.check(
        "Canonical Form Exists",
        isinstance(canonical, tuple)
        and canonical[0] == "STRUCT3D_CANONICAL_FORM",
    )

    # ========================================================
    # 3. Reflexivity
    # ========================================================

    suite.section("Canonical Reflexivity")

    c1 = structural_canonical_form(world)
    c2 = structural_canonical_form(world.copy())

    print(
        "Canonical(W) == Canon(W):",
        c1 == c2,
    )

    suite.check(
        "Canonical Reflexivity",
        c1 == c2,
    )

    # ========================================================
    # 4. Dictionary Order Invariance
    # ========================================================

    suite.section("Dictionary Order Invariance")

    reordered = World(
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

    h_original = canonical_hash(world)
    h_reordered = canonical_hash(reordered)

    print(
        "Original hash:",
        h_original,
    )

    print(
        "Reordered hash:",
        h_reordered,
    )

    suite.check(
        "Dictionary Order Invariance",
        h_original == h_reordered,
    )

    # ========================================================
    # 5. Unit Relabeling
    # ========================================================

    suite.section("Unit Relabeling Canonical Invariance")

    unit_perm = [1, 0, 3, 2]

    relabeled_units = relabel_world(
        world,
        unit_perm=unit_perm,
    )

    print(
        "Unit permutation:",
        unit_perm,
    )

    print(
        "Original hash:",
        canonical_hash(world),
    )

    print(
        "Relabeled hash:",
        canonical_hash(relabeled_units),
    )

    suite.check(
        "Unit Relabeling Invariance",
        canonical_hash(world)
        == canonical_hash(relabeled_units),
    )

    # ========================================================
    # 6. Object Relabeling
    # ========================================================

    suite.section("Object Relabeling Canonical Invariance")

    object_perm = [1, 0]

    relabeled_objects = relabel_world(
        world,
        object_perm=object_perm,
    )

    suite.check(
        "Object Relabeling Invariance",
        canonical_hash(world)
        == canonical_hash(relabeled_objects),
    )

    # ========================================================
    # 7. Combined Relabeling
    # ========================================================

    suite.section("Combined Relabeling Canonical Invariance")

    combined = relabel_world(
        world,
        unit_perm=[1, 0, 3, 2],
        object_perm=[1, 0],
        instance_perm=[1, 0],
        relation_perm=[1, 0],
    )

    print(
        "Combined canonical hash:",
        canonical_hash(combined),
    )

    suite.check(
        "Combined Relabeling Invariance",
        canonical_hash(world)
        == canonical_hash(combined),
    )

    # ========================================================
    # 8. Quotient / Canonical Agreement
    # ========================================================

    suite.section("Quotient / Canonical Agreement")

    q1 = structural_quotient(world)
    q2 = structural_quotient(combined)

    print(
        "Original quotient hash:",
        quotient_hash(world),
    )

    print(
        "Relabeled quotient hash:",
        quotient_hash(combined),
    )

    suite.check(
        "Quotient Canonical Invariance",
        q1 == q2,
    )

    # ========================================================
    # 9. Canonical Idempotence
    # ========================================================

    suite.section("Canonical Idempotence")

    # A canonical representation must already be ordered.
    canonical_again = freeze(canonical)

    suite.check(
        "Canonical Idempotence",
        canonical_again == freeze(
            structural_canonical_form(world)
        ),
    )

    # ========================================================
    # 10. Explicit Automorphism Compatibility
    # ========================================================

    suite.section("Automorphism Compatibility")

    automorphisms = enumerate_automorphisms(
        world,
        max_tests=100000,
    )

    print(
        "Automorphisms tested:",
        len(automorphisms),
    )

    all_preserve = True

    base_hash = canonical_hash(world)

    for (
        up,
        op,
        ip,
        rp,
    ) in automorphisms:

        transformed = relabel_world(
            world,
            unit_perm=up,
            object_perm=op,
            instance_perm=ip,
            relation_perm=rp,
        )

        if canonical_hash(transformed) != base_hash:
            all_preserve = False
            break

    suite.check(
        "All Automorphisms Preserve Canonical Form",
        all_preserve,
    )

    # ========================================================
    # 11. Structural Mutation Must Change Canonical Form
    # ========================================================

    suite.section("Structural Mutation")

    mutated = world.copy()

    mutated.units[0].primitive = Primitive(
        "cylinder",
        {
            "scale": 1.0,
            "fit": 0.1,
        },
    )

    original_mut_hash = canonical_hash(world)
    mutated_hash = canonical_hash(mutated)

    print(
        "Original canonical hash:",
        original_mut_hash,
    )

    print(
        "Mutated canonical hash:",
        mutated_hash,
    )

    suite.check(
        "Structural Mutation Changes Canonical Form",
        original_mut_hash != mutated_hash,
    )

    # ========================================================
    # 12. Isomorphism <=> Canonical Equality
    # ========================================================

    suite.section(
        "Isomorphism iff Canonical Equality"
    )

    W1 = world

    W2 = relabel_world(
        world,
        unit_perm=[1, 0, 3, 2],
        object_perm=[1, 0],
        instance_perm=[1, 0],
        relation_perm=[1, 0],
    )

    W3 = mutated

    iso_positive = (
        canonical_hash(W1)
        ==
        canonical_hash(W2)
    )

    iso_negative = (
        canonical_hash(W1)
        !=
        canonical_hash(W3)
    )

    print(
        "W1 ~ W2:",
        iso_positive,
    )

    print(
        "W1 ~ W3:",
        iso_negative,
    )

    suite.check(
        "Isomorphism -> Canonical Equality",
        iso_positive,
    )

    suite.check(
        "Non-Isomorphism -> Canonical Inequality",
        iso_negative,
    )

    # ========================================================
    # Summary
    # ========================================================

    suite.summary()


if __name__ == "__main__":
    main()