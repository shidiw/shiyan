# ============================================================
# Struct3D v3.3
# experiments/v33/run_v33_structural_isomorphism.py
#
# Structural Isomorphism Regression Suite
#
# CPU only
# ============================================================

from __future__ import annotations

import os
import sys
import copy

import numpy as np


# ============================================================
# ROOT
# ============================================================

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from structure.world_state import WorldState
from structure.structural_isomorphism import (
    structural_isomorphic
)


# ============================================================
# Constants
# ============================================================

VERSION = "3.3"
SEED = 20260814


# ============================================================
# Utility
# ============================================================

def section(title):

    print()
    print("-" * 60)
    print(title)
    print("-" * 60)


def deep_copy_world(world):

    return copy.deepcopy(world)


# ============================================================
# Geometry
# ============================================================

def make_sphere(
    center,
    radius,
    n,
    seed
):

    rng = np.random.default_rng(seed)

    dirs = rng.normal(
        size=(n, 3)
    )

    dirs /= (
        np.linalg.norm(
            dirs,
            axis=1,
            keepdims=True
        )
        +
        1e-12
    )

    return (
        np.asarray(
            center,
            dtype=float
        )
        +
        radius * dirs
    )


# ============================================================
# Base world
# ============================================================

def build_base_world():

    world = WorldState()

    radii = [
        1.0,
        0.8,
        0.7,
        0.9,
        0.8
    ]

    centers = [
        [0.0, 0.0, 0.0],
        [2.5, 0.0, 0.0],
        [5.0, 0.0, 0.0],
        [8.0, 0.0, 0.0],
        [10.5, 0.0, 0.0]
    ]

    for i in range(5):

        world.add_unit({

            "id": i,

            "points": make_sphere(
                centers[i],
                radii[i],
                100,
                10 * (i + 1)
            ),

            "primitive": "sphere",

            "parameters": {
                "radius": radii[i]
            },

            "energy": {
                "value": 0.1 + 0.1 * i
            }
        })

    world.add_object({

        "id": 0,
        "type": "assembly",
        "parts": [0, 1],

        "relations": [
            {
                "source": 0,
                "target": 1,
                "type": "connected"
            }
        ]
    })

    world.add_object({

        "id": 1,
        "type": "single",
        "parts": [2],
        "relations": []
    })

    world.add_object({

        "id": 2,
        "type": "assembly",
        "parts": [3, 4],

        "relations": [
            {
                "source": 3,
                "target": 4,
                "type": "connected"
            }
        ]
    })

    world.add_instance({

        "id": 0,
        "object": 0,
        "parts": [0, 1]
    })

    world.add_instance({

        "id": 1,
        "object": 1,
        "parts": [2]
    })

    world.add_instance({

        "id": 2,
        "object": 2,
        "parts": [3, 4]
    })

    world.add_relation({

        "source": 0,
        "target": 1,
        "type": "connected",
        "confidence": 1.0
    })

    world.add_relation({

        "source": 1,
        "target": 2,
        "type": "connected",
        "confidence": 1.0
    })

    world.add_relation({

        "source": 0,
        "target": 2,
        "type": "adjacent",
        "confidence": 0.8
    })

    return world


# ============================================================
# Unit permutation
# ============================================================

def permute_units(
    world,
    permutation
):

    source = deep_copy_world(world)

    result = WorldState()

    old_to_new = {}

    for new_id, old_id in enumerate(permutation):

        old_to_new[int(old_id)] = new_id

        unit = copy.deepcopy(
            source.units[old_id]
        )

        unit["id"] = new_id

        result.add_unit(unit)

    for object_id, obj in source.objects.items():

        new_obj = copy.deepcopy(obj)

        new_obj["parts"] = [

            old_to_new[int(uid)]

            for uid in obj.get(
                "parts",
                []
            )
        ]

        for relation in new_obj.get(
            "relations",
            []
        ):

            relation["source"] = old_to_new[
                int(relation["source"])
            ]

            relation["target"] = old_to_new[
                int(relation["target"])
            ]

        result.add_object(new_obj)

    for instance in source.instances.values():

        new_instance = copy.deepcopy(
            instance
        )

        new_instance["parts"] = [

            old_to_new[int(uid)]

            for uid in instance.get(
                "parts",
                []
            )
        ]

        result.add_instance(
            new_instance
        )

    for relation in source.relations:

        result.add_relation(
            copy.deepcopy(relation)
        )

    return result


# ============================================================
# Object permutation
# ============================================================

def permute_objects(
    world,
    permutation
):

    source = deep_copy_world(world)

    result = WorldState()

    old_to_new = {
        int(old): new
        for new, old in enumerate(permutation)
    }

    for unit in source.units.values():

        result.add_unit(
            copy.deepcopy(unit)
        )

    for new_id, old_id in enumerate(permutation):

        obj = copy.deepcopy(
            source.objects[old_id]
        )

        obj["id"] = new_id

        result.add_object(obj)

    for instance in source.instances.values():

        new_instance = copy.deepcopy(
            instance
        )

        new_instance["object"] = old_to_new[
            int(instance["object"])
        ]

        result.add_instance(
            new_instance
        )

    for relation in source.relations:

        r = copy.deepcopy(relation)

        r["source"] = old_to_new[
            int(r["source"])
        ]

        r["target"] = old_to_new[
            int(r["target"])
        ]

        result.add_relation(r)

    return result


# ============================================================
# Instance permutation
# ============================================================

def permute_instances(
    world,
    permutation
):

    source = deep_copy_world(world)

    result = WorldState()

    for unit in source.units.values():

        result.add_unit(
            copy.deepcopy(unit)
        )

    for obj in source.objects.values():

        result.add_object(
            copy.deepcopy(obj)
        )

    for new_id, old_id in enumerate(permutation):

        instance = copy.deepcopy(
            source.instances[old_id]
        )

        instance["id"] = new_id

        result.add_instance(instance)

    for relation in source.relations:

        result.add_relation(
            copy.deepcopy(relation)
        )

    return result


# ============================================================
# Relation permutation
# ============================================================

def permute_relations(
    world,
    permutation
):

    result = deep_copy_world(world)

    relations = [

        copy.deepcopy(
            result.relations[i]
        )

        for i in permutation
    ]

    result.relations = relations

    return result


# ============================================================
# Rigid transform
# ============================================================

def rotation_matrix_z(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0]
    ])


def transform_points(
    points,
    R,
    t
):

    points = np.asarray(
        points,
        dtype=float
    )

    center = np.mean(
        points,
        axis=0
    )

    X = points - center

    return (
        X @ R.T
        +
        center
        +
        np.asarray(
            t,
            dtype=float
        )
    )


def rigid_transform_world(
    world,
    R,
    t
):

    result = deep_copy_world(world)

    for unit in result.units.values():

        unit["points"] = transform_points(
            unit["points"],
            R,
            t
        )

    return result


# ============================================================
# Equivalent check
# ============================================================

def check_isomorphic(
    name,
    world_a,
    world_b
):

    result = structural_isomorphic(
        world_a,
        world_b
    )

    print()
    print(name)
    print(
        "Structural isomorphic:",
        result
    )

    print(
        "[{}] {}".format(
            "PASS" if result else "FAIL",
            name
        )
    )

    return result


# ============================================================
# Non-isomorphic check
# ============================================================

def check_non_isomorphic(
    name,
    world_a,
    world_b
):

    result = structural_isomorphic(
        world_a,
        world_b
    )

    passed = not result

    print()
    print(name)
    print(
        "Structural isomorphic:",
        result
    )

    print(
        "[{}] {}".format(
            "PASS" if passed else "FAIL",
            name
        )
    )

    return passed


# ============================================================
# Mutations
# ============================================================

def mutate_primitive(world):

    result = deep_copy_world(world)

    result.units[0]["primitive"] = "cube"

    return result


def mutate_relation_type(world):

    result = deep_copy_world(world)

    result.relations[0]["type"] = "contact"

    return result


def mutate_relation_confidence(world):

    result = deep_copy_world(world)

    result.relations[0]["confidence"] = 0.25

    return result


def mutate_object_composition(world):

    result = deep_copy_world(world)

    result.objects[0]["parts"] = [0]

    return result


def delete_relation(world):

    result = deep_copy_world(world)

    result.relations = result.relations[:-1]

    return result


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v3.3 Structural Isomorphism Regression Suite"
    )
    print("=" * 60)

    print(
        "Version:",
        VERSION
    )

    print(
        "Seed:",
        SEED
    )

    rng = np.random.default_rng(SEED)

    results = []

    # --------------------------------------------------------
    # Base
    # --------------------------------------------------------

    section("[1] Base World")

    world = build_base_world()

    validation = world.validate()

    ok = validation["valid"]

    print(
        "[{}] World Validation".format(
            "PASS" if ok else "FAIL"
        )
    )

    results.append(
        ("World Validation", ok)
    )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    section("Structural Identity")

    ok = structural_isomorphic(
        world,
        world
    )

    print(
        "W ≅ W:",
        ok
    )

    results.append(
        ("Reflexive Isomorphism", ok)
    )

    # --------------------------------------------------------
    # Unit relabeling
    # --------------------------------------------------------

    section("Unit Relabeling")

    permutation = rng.permutation(
        len(world.units)
    ).tolist()

    print(
        "Permutation:",
        permutation
    )

    candidate = permute_units(
        world,
        permutation
    )

    ok = check_isomorphic(
        "Unit Relabeling Isomorphism",
        world,
        candidate
    )

    results.append(
        ("Unit Relabeling Isomorphism", ok)
    )

    # --------------------------------------------------------
    # Object relabeling
    # --------------------------------------------------------

    section("Object Relabeling")

    permutation = rng.permutation(
        len(world.objects)
    ).tolist()

    print(
        "Permutation:",
        permutation
    )

    candidate = permute_objects(
        world,
        permutation
    )

    ok = check_isomorphic(
        "Object Relabeling Isomorphism",
        world,
        candidate
    )

    results.append(
        ("Object Relabeling Isomorphism", ok)
    )

    # --------------------------------------------------------
    # Instance relabeling
    # --------------------------------------------------------

    section("Instance Relabeling")

    permutation = rng.permutation(
        len(world.instances)
    ).tolist()

    print(
        "Permutation:",
        permutation
    )

    candidate = permute_instances(
        world,
        permutation
    )

    ok = check_isomorphic(
        "Instance Relabeling Isomorphism",
        world,
        candidate
    )

    results.append(
        ("Instance Relabeling Isomorphism", ok)
    )

    # --------------------------------------------------------
    # Relation relabeling
    # --------------------------------------------------------

    section("Relation Relabeling")

    permutation = rng.permutation(
        len(world.relations)
    ).tolist()

    print(
        "Permutation:",
        permutation
    )

    candidate = permute_relations(
        world,
        permutation
    )

    ok = check_isomorphic(
        "Relation Relabeling Isomorphism",
        world,
        candidate
    )

    results.append(
        ("Relation Relabeling Isomorphism", ok)
    )

    # --------------------------------------------------------
    # Combined
    # --------------------------------------------------------

    section(
        "Combined Structural Isomorphism"
    )

    candidate = permute_units(
        world,
        rng.permutation(
            len(world.units)
        ).tolist()
    )

    candidate = permute_objects(
        candidate,
        rng.permutation(
            len(candidate.objects)
        ).tolist()
    )

    candidate = permute_instances(
        candidate,
        rng.permutation(
            len(candidate.instances)
        ).tolist()
    )

    candidate = permute_relations(
        candidate,
        rng.permutation(
            len(candidate.relations)
        ).tolist()
    )

    ok = check_isomorphic(
        "Combined Structural Isomorphism",
        world,
        candidate
    )

    results.append(
        ("Combined Structural Isomorphism", ok)
    )

    # --------------------------------------------------------
    # Combined + rigid
    # --------------------------------------------------------

    section(
        "Combined Isomorphism + Rigid Transform"
    )

    theta = rng.uniform(
        -np.pi,
        np.pi
    )

    R = rotation_matrix_z(theta)

    t = rng.uniform(
        -100.0,
        100.0,
        size=3
    )

    candidate = rigid_transform_world(
        candidate,
        R,
        t
    )

    print(
        "Rigid rotation determinant:",
        "{:.12f}".format(
            np.linalg.det(R)
        )
    )

    print(
        "Rigid translation:",
        np.round(
            t,
            6
        )
    )

    ok = check_isomorphic(
        "Combined Isomorphism + Rigid Transform",
        world,
        candidate
    )

    results.append(
        (
            "Combined Isomorphism + Rigid Transform",
            ok
        )
    )

    # --------------------------------------------------------
    # Negative primitive
    # --------------------------------------------------------

    section(
        "Structural Non-Isomorphism: Primitive"
    )

    candidate = mutate_primitive(world)

    ok = check_non_isomorphic(
        "Primitive Mutation",
        world,
        candidate
    )

    results.append(
        ("Primitive Mutation", ok)
    )

    # --------------------------------------------------------
    # Negative object composition
    # --------------------------------------------------------

    section(
        "Structural Non-Isomorphism: Object Composition"
    )

    candidate = mutate_object_composition(world)

    ok = check_non_isomorphic(
        "Object Composition Mutation",
        world,
        candidate
    )

    results.append(
        ("Object Composition Mutation", ok)
    )

    # --------------------------------------------------------
    # Negative relation type
    # --------------------------------------------------------

    section(
        "Structural Non-Isomorphism: Relation Type"
    )

    candidate = mutate_relation_type(world)

    ok = check_non_isomorphic(
        "Relation Type Mutation",
        world,
        candidate
    )

    results.append(
        ("Relation Type Mutation", ok)
    )

    # --------------------------------------------------------
    # Negative confidence
    # --------------------------------------------------------

    section(
        "Structural Non-Isomorphism: Relation Confidence"
    )

    candidate = mutate_relation_confidence(world)

    ok = check_non_isomorphic(
        "Relation Confidence Mutation",
        world,
        candidate
    )

    results.append(
        ("Relation Confidence Mutation", ok)
    )

    # --------------------------------------------------------
    # Negative deletion
    # --------------------------------------------------------

    section(
        "Structural Non-Isomorphism: Relation Deletion"
    )

    candidate = delete_relation(world)

    ok = check_non_isomorphic(
        "Relation Deletion",
        world,
        candidate
    )

    results.append(
        ("Relation Deletion", ok)
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v3.3")
    print("=" * 60)

    passed = sum(
        1
        for _, ok in results
        if ok
    )

    total = len(results)

    failed = total - passed

    for name, ok in results:

        print(
            "{:<50} {}".format(
                name + ":",
                "PASS" if ok else "FAIL"
            )
        )

    print()
    print(
        "Total tests:",
        total
    )

    print(
        "Passed:",
        passed
    )

    print(
        "Failed:",
        failed
    )

    print()

    print(
        "STATUS:",
        "PASS" if failed == 0 else "FAIL"
    )

    print("=" * 60)


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":
    main()