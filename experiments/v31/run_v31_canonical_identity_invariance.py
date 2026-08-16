# ============================================================
# Struct3D v3.1
# experiments/v31/run_v31_canonical_identity_invariance.py
#
# Canonical Identity Invariance
#
# Core principle:
#
#     Structurally equivalent worlds
#         ->
#     identical canonical identity
#
#     Structurally different worlds
#         ->
#     different canonical identity
#
# v3.0 already validated:
#
#     rigid invariance
#     unit permutation
#     relation permutation
#     entity order permutation
#     persistence
#     deterministic replay
#
# v3.1 upgrades this into:
#
#     Canonical Identity
#
# Positive tests:
#
#     equivalent worlds -> same identity
#
# Negative tests:
#
#     structural mutation -> different identity
#
# CPU only
# ============================================================

import os
import sys
import copy
import hashlib
import pickle

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


# ============================================================
# Constants
# ============================================================

VERSION = "3.1"
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
# Canonical Identity
# ============================================================

def canonical_signature(world):

    return world.canonical_signature()


def canonical_payload(world):

    return world.canonical_payload()


def canonical_hash(world):

    payload = canonical_payload(world)

    data = pickle.dumps(
        payload,
        protocol=4
    )

    return hashlib.sha256(
        data
    ).hexdigest()


def identity(world):

    return canonical_hash(world)


# ============================================================
# Rotation
# ============================================================

def rotation_matrix_x(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, c, -s],
        [0.0, s, c]
    ])


def rotation_matrix_y(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, 0.0, s],
        [0.0, 1.0, 0.0],
        [-s, 0.0, c]
    ])


def rotation_matrix_z(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0]
    ])


def random_rotation(rng):

    ax = rng.uniform(
        -np.pi,
        np.pi
    )

    ay = rng.uniform(
        -np.pi,
        np.pi
    )

    az = rng.uniform(
        -np.pi,
        np.pi
    )

    Rx = rotation_matrix_x(ax)
    Ry = rotation_matrix_y(ay)
    Rz = rotation_matrix_z(az)

    return (
        Rz
        @
        Ry
        @
        Rx
    )


# ============================================================
# Geometry
# ============================================================

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


# ============================================================
# Sphere
# ============================================================

def make_sphere(
    center,
    radius,
    n,
    seed
):

    rng = np.random.default_rng(
        seed
    )

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
# Base World Construction
# ============================================================

def build_base_world():

    world = WorldState()

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    unit_points = [

        make_sphere(
            center=[0.0, 0.0, 0.0],
            radius=1.0,
            n=100,
            seed=10
        ),

        make_sphere(
            center=[2.5, 0.0, 0.0],
            radius=0.8,
            n=100,
            seed=20
        ),

        make_sphere(
            center=[5.0, 0.0, 0.0],
            radius=0.7,
            n=100,
            seed=30
        ),

        make_sphere(
            center=[8.0, 0.0, 0.0],
            radius=0.9,
            n=100,
            seed=40
        ),

        make_sphere(
            center=[10.5, 0.0, 0.0],
            radius=0.8,
            n=100,
            seed=50
        )
    ]

    for i, points in enumerate(
        unit_points
    ):

        world.add_unit({

            "id": i,

            "points": points,

            "primitive": "sphere",

            "parameters": {

                "radius":
                    [
                        1.0,
                        0.8,
                        0.7,
                        0.9,
                        0.8
                    ][i]

            },

            "energy": {

                "value":
                    0.1
                    +
                    0.1 * i
            }

        })

    # --------------------------------------------------------
    # Objects
    #
    # Object 0 = units 0,1
    # Object 1 = unit 2
    # Object 2 = units 3,4
    #
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # World relations
    #
    # Object 0 -> Object 1
    # Object 1 -> Object 2
    # Object 0 -> Object 2
    #
    # --------------------------------------------------------

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
# World Statistics
# ============================================================

def print_world_statistics(
    world
):

    stats = world.canonical_statistics()

    print(
        "Units:",
        stats["units"]
    )

    print(
        "Objects:",
        stats["objects"]
    )

    print(
        "Instances:",
        stats["instances"]
    )

    print(
        "Relations:",
        stats["relations"]
    )

    print(
        "Canonical Statistics:",
        stats
    )

    print(
        "Canonical Hash:",
        canonical_hash(world)
    )


# ============================================================
# World Validation
# ============================================================

def test_validation(
    world
):

    result = world.validate()

    passed = bool(
        result.get(
            "valid",
            False
        )
    )

    print(
        "[{}] World Validation".format(
            "PASS"
            if passed
            else "FAIL"
        )
    )

    if not passed:

        print(
            "Errors:",
            result.get(
                "errors",
                []
            )
        )

    return passed


# ============================================================
# Canonical Signature Sanity
# ============================================================

def test_signature_sanity(
    world
):

    signature = canonical_signature(
        world
    )

    exists = (
        signature is not None
    )

    pickle_safe = True

    try:

        pickle.dumps(
            canonical_payload(
                world
            ),
            protocol=4
        )

    except Exception:

        pickle_safe = False

    passed = (
        exists
        and
        pickle_safe
    )

    print(
        "Signature exists:",
        exists
    )

    print(
        "Canonical payload pickle-safe:",
        pickle_safe
    )

    print(
        "[{}] Canonical Identity Sanity".format(
            "PASS"
            if passed
            else "FAIL"
        )
    )

    return passed


# ============================================================
# Equivalent World Comparison
# ============================================================

def compare_equivalent(
    name,
    world_a,
    world_b
):

    sig_a = canonical_signature(
        world_a
    )

    sig_b = canonical_signature(
        world_b
    )

    hash_a = canonical_hash(
        world_a
    )

    hash_b = canonical_hash(
        world_b
    )

    canonical_equal = (
        sig_a == sig_b
    )

    hash_equal = (
        hash_a == hash_b
    )

    passed = (
        canonical_equal
        and
        hash_equal
    )

    print()
    print(name)

    print(
        "Canonical equal:",
        canonical_equal
    )

    print(
        "Hash equal:",
        hash_equal
    )

    # ========================================================
    # DEBUG
    # ========================================================

    if not canonical_equal:

        print()
        print("******** CANONICAL PAYLOAD DIFF ********")

        print()
        print(
            "Payload A type:",
            type(sig_a)
        )

        print(
            "Payload B type:",
            type(sig_b)
        )

        if isinstance(sig_a, dict):

            keys = sorted(
                set(sig_a.keys())
                |
                set(sig_b.keys()),
                key=str
            )

            for key in keys:

                a = sig_a.get(
                    key,
                    "<MISSING>"
                )

                b = sig_b.get(
                    key,
                    "<MISSING>"
                )

                if a != b:

                    print()
                    print(
                        "DIFF KEY:",
                        key
                    )

                    print()
                    print(
                        "A:"
                    )

                    print(
                        repr(a)
                    )

                    print()
                    print(
                        "B:"
                    )

                    print(
                        repr(b)
                    )

        else:

            print()
            print("A:")
            print(repr(sig_a))

            print()
            print("B:")
            print(repr(sig_b))

        print()
        print(
            "******** END PAYLOAD DIFF ********"
        )

    print(
        "[{}] {}".format(
            "PASS"
            if passed
            else "FAIL",
            name
        )
    )

    return passed


# ============================================================
# Non-Equivalent World Comparison
# ============================================================

def compare_non_equivalent(
    name,
    world_a,
    world_b
):

    hash_a = canonical_hash(
        world_a
    )

    hash_b = canonical_hash(
        world_b
    )

    canonical_equal = (
        canonical_signature(
            world_a
        )
        ==
        canonical_signature(
            world_b
        )
    )

    hash_equal = (
        hash_a == hash_b
    )

    passed = (
        not canonical_equal
        and
        not hash_equal
    )

    print()
    print(name)

    print(
        "Canonical equal:",
        canonical_equal
    )

    print(
        "Hash equal:",
        hash_equal
    )

    print(
        "[{}] {}".format(
            "PASS"
            if passed
            else "FAIL",
            name
        )
    )

    return passed


# ============================================================
# Rigid Transform
# ============================================================

def rigid_transform_world(
    world,
    R,
    t
):

    transformed = deep_copy_world(
        world
    )

    for unit in transformed.units.values():

        points = np.asarray(
            unit["points"],
            dtype=float
        )

        unit["points"] = transform_points(
            points,
            R,
            t
        )

    return transformed


# ============================================================
# Unit Permutation
# ============================================================

def permute_units(
    world,
    permutation
):

    source = deep_copy_world(
        world
    )

    result = WorldState()

    # ========================================================
    # Unit permutation
    #
    # permutation[new_id] = old_id
    #
    # Therefore:
    #
    # old_unit_id -> new_unit_id
    # ========================================================

    old_to_new = {}

    for new_id, old_id in enumerate(
        permutation
    ):

        old_to_new[
            int(old_id)
        ] = int(new_id)

    # ========================================================
    # Units
    # ========================================================

    old_units = list(
        source.units.values()
    )

    for new_id, old_id in enumerate(
        permutation
    ):

        unit = copy.deepcopy(
            old_units[
                int(old_id)
            ]
        )

        unit["id"] = int(new_id)

        result.add_unit(
            unit
        )

    # ========================================================
    # Objects
    #
    # Object IDs DO NOT change.
    #
    # Only object.parts contains Unit IDs,
    # so only those references need remapping.
    # ========================================================

    for object_id, obj in source.objects.items():

        new_obj = copy.deepcopy(
            obj
        )

        if "parts" in new_obj:

            new_obj["parts"] = [

                old_to_new[
                    int(unit_id)
                ]

                for unit_id in new_obj[
                    "parts"
                ]

            ]

        # ----------------------------------------------------
        # Object-local relations
        #
        # These relations refer to Units.
        # Therefore they MUST be remapped.
        # ----------------------------------------------------

        if "relations" in new_obj:

            new_relations = []

            for relation in new_obj[
                "relations"
            ]:

                r = copy.deepcopy(
                    relation
                )

                if "source" in r:

                    r["source"] = old_to_new[
                        int(
                            r["source"]
                        )
                    ]

                if "target" in r:

                    r["target"] = old_to_new[
                        int(
                            r["target"]
                        )
                    ]

                new_relations.append(
                    r
                )

            new_obj[
                "relations"
            ] = new_relations

        result.add_object(
            new_obj
        )

    # ========================================================
    # Instances
    #
    # Instance IDs and Object IDs remain unchanged.
    #
    # instance.parts contains Unit IDs.
    # Therefore those references must be remapped.
    # ========================================================

    for instance_id, instance in source.instances.items():

        new_instance = copy.deepcopy(
            instance
        )

        if "parts" in new_instance:

            new_instance[
                "parts"
            ] = [

                old_to_new[
                    int(unit_id)
                ]

                for unit_id in new_instance[
                    "parts"
                ]

            ]

        result.add_instance(
            new_instance
        )

    # ========================================================
    # World relations
    #
    # IMPORTANT:
    #
    # World relations refer to OBJECT IDs,
    # NOT Unit IDs.
    #
    # Unit permutation therefore MUST NOT modify them.
    # ========================================================

    for relation in source.relations:

        result.add_relation(
            copy.deepcopy(
                relation
            )
        )

    return result


# ============================================================
# Relation Permutation
# ============================================================

def permute_relations(
    world,
    permutation
):

    result = deep_copy_world(
        world
    )

    relations = [
        copy.deepcopy(r)
        for r in result.relations
    ]

    result.relations = [
        relations[i]
        for i in permutation
    ]

    return result


# ============================================================
# Dictionary Order Permutation
# ============================================================

def reverse_dictionary_order(
    world
):

    result = deep_copy_world(
        world
    )

    result.units = dict(
        reversed(
            list(
                result.units.items()
            )
        )
    )

    result.objects = dict(
        reversed(
            list(
                result.objects.items()
            )
        )
    )

    result.instances = dict(
        reversed(
            list(
                result.instances.items()
            )
        )
    )

    result.relations = list(
        reversed(
            result.relations
        )
    )

    return result


# ============================================================
# Combined Permutation
# ============================================================

def combined_permutation(
    world,
    unit_perm,
    relation_perm
):

    result = permute_units(
        world,
        unit_perm
    )

    result = permute_relations(
        result,
        relation_perm
    )

    result = reverse_dictionary_order(
        result
    )

    return result


# ============================================================
# Mutation Helpers
# ============================================================

def mutate_primitive(
    world
):

    result = deep_copy_world(
        world
    )

    result.units[
        0
    ]["primitive"] = "cube"

    return result


def mutate_relation_type(
    world
):

    result = deep_copy_world(
        world
    )

    result.relations[
        0
    ]["type"] = "contact"

    return result


def mutate_relation_confidence(
    world
):

    result = deep_copy_world(
        world
    )

    result.relations[
        0
    ]["confidence"] = 0.25

    return result


def delete_relation(
    world
):

    result = deep_copy_world(
        world
    )

    result.relations = result.relations[
        :-1
    ]

    return result


def mutate_object_composition(
    world
):

    result = deep_copy_world(
        world
    )

    result.objects[
        0
    ]["parts"] = [0]

    return result


def mutate_instance_composition(
    world
):

    result = deep_copy_world(
        world
    )

    result.instances[
        0
    ]["parts"] = [0]

    return result


def delete_unit(
    world
):

    result = deep_copy_world(
        world
    )

    result.units.pop(
        4
    )

    return result


def mutate_object_type(
    world
):

    result = deep_copy_world(
        world
    )

    result.objects[
        0
    ]["type"] = "single"

    return result


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v3.1 Canonical Identity Regression Suite"
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

    rng = np.random.default_rng(
        SEED
    )

    results = []


    # ========================================================
    # Base
    # ========================================================

    section(
        "[1] Base World"
    )

    world = build_base_world()

    print_world_statistics(
        world
    )

    ok = test_validation(
        world
    )

    results.append(
        (
            "World Validation",
            ok
        )
    )


    # ========================================================
    # Sanity
    # ========================================================

    section(
        "Canonical Identity Sanity"
    )

    ok = test_signature_sanity(
        world
    )

    results.append(
        (
            "Canonical Identity Sanity",
            ok
        )
    )


    # ========================================================
    # Positive: Rigid Transform
    # ========================================================

    section(
        "Rigid Transform Identity Invariance"
    )

    R = random_rotation(
        rng
    )

    t = rng.uniform(
        -50.0,
        50.0,
        size=3
    )

    transformed = rigid_transform_world(
        world,
        R,
        t
    )

    ok = compare_equivalent(
        "Rigid Transform Identity Invariance",
        world,
        transformed
    )

    results.append(
        (
            "Rigid Transform Identity Invariance",
            ok
        )
    )


    # ========================================================
    # Positive: Unit Permutation
    # ========================================================

    section(
        "Unit Identity Permutation"
    )

    unit_perm = rng.permutation(
        5
    ).tolist()

    print(
        "Permutation:",
        unit_perm
    )

    permuted = permute_units(
        world,
        unit_perm
    )

    ok = compare_equivalent(
        "Unit Identity Permutation",
        world,
        permuted
    )

    results.append(
        (
            "Unit Identity Permutation",
            ok
        )
    )


    # ========================================================
    # Positive: Relation Permutation
    # ========================================================

    section(
        "Relation Identity Permutation"
    )

    relation_perm = rng.permutation(
        len(
            world.relations
        )
    ).tolist()

    print(
        "Permutation:",
        relation_perm
    )

    permuted = permute_relations(
        world,
        relation_perm
    )

    ok = compare_equivalent(
        "Relation Identity Permutation",
        world,
        permuted
    )

    results.append(
        (
            "Relation Identity Permutation",
            ok
        )
    )


    # ========================================================
    # Positive: Dictionary Order
    # ========================================================

    section(
        "Dictionary Order Invariance"
    )

    reordered = reverse_dictionary_order(
        world
    )

    ok = compare_equivalent(
        "Dictionary Order Invariance",
        world,
        reordered
    )

    results.append(
        (
            "Dictionary Order Invariance",
            ok
        )
    )


    # ========================================================
    # Positive: Combined
    # ========================================================

    section(
        "Combined Identity Permutation"
    )

    unit_perm = rng.permutation(
        5
    ).tolist()

    relation_perm = rng.permutation(
        len(
            world.relations
        )
    ).tolist()

    print(
        "Unit permutation:",
        unit_perm
    )

    print(
        "Relation permutation:",
        relation_perm
    )

    combined = combined_permutation(
        world,
        unit_perm,
        relation_perm
    )

    ok = compare_equivalent(
        "Combined Identity Permutation",
        world,
        combined
    )

    results.append(
        (
            "Combined Identity Permutation",
            ok
        )
    )


    # ========================================================
    # Positive: Combined + Rigid
    # ========================================================

    section(
        "Combined Identity Permutation + Rigid Transform"
    )

    R = random_rotation(
        rng
    )

    t = rng.uniform(
        -100.0,
        100.0,
        size=3
    )

    transformed = rigid_transform_world(
        combined,
        R,
        t
    )

    ok = compare_equivalent(
        "Combined Identity Permutation + Rigid Transform",
        world,
        transformed
    )

    results.append(
        (
            "Combined Identity Permutation + Rigid Transform",
            ok
        )
    )


    # ========================================================
    # Negative: Primitive
    # ========================================================

    section(
        "Structural Mutation: Primitive"
    )

    mutated = mutate_primitive(
        world
    )

    ok = compare_non_equivalent(
        "Primitive Mutation",
        world,
        mutated
    )

    results.append(
        (
            "Primitive Mutation",
            ok
        )
    )


    # ========================================================
    # Negative: Relation Type
    # ========================================================

    section(
        "Structural Mutation: Relation Type"
    )

    mutated = mutate_relation_type(
        world
    )

    ok = compare_non_equivalent(
        "Relation Type Mutation",
        world,
        mutated
    )

    results.append(
        (
            "Relation Type Mutation",
            ok
        )
    )


    # ========================================================
    # Negative: Relation Confidence
    # ========================================================

    section(
        "Structural Mutation: Relation Confidence"
    )

    mutated = mutate_relation_confidence(
        world
    )

    ok = compare_non_equivalent(
        "Relation Confidence Mutation",
        world,
        mutated
    )

    results.append(
        (
            "Relation Confidence Mutation",
            ok
        )
    )


    # ========================================================
    # Negative: Delete Relation
    # ========================================================

    section(
        "Structural Mutation: Relation Deletion"
    )

    mutated = delete_relation(
        world
    )

    ok = compare_non_equivalent(
        "Relation Deletion",
        world,
        mutated
    )

    results.append(
        (
            "Relation Deletion",
            ok
        )
    )


    # ========================================================
    # Negative: Object Composition
    # ========================================================

    section(
        "Structural Mutation: Object Composition"
    )

    mutated = mutate_object_composition(
        world
    )

    ok = compare_non_equivalent(
        "Object Composition Mutation",
        world,
        mutated
    )

    results.append(
        (
            "Object Composition Mutation",
            ok
        )
    )


    # ========================================================
    # Negative: Instance Composition
    # ========================================================

    section(
        "Structural Mutation: Instance Composition"
    )

    mutated = mutate_instance_composition(
        world
    )

    ok = compare_non_equivalent(
        "Instance Composition Mutation",
        world,
        mutated
    )

    results.append(
        (
            "Instance Composition Mutation",
            ok
        )
    )


    # ========================================================
    # Negative: Unit Deletion
    # ========================================================

    section(
        "Structural Mutation: Unit Deletion"
    )

    mutated = delete_unit(
        world
    )

    ok = compare_non_equivalent(
        "Unit Deletion",
        world,
        mutated
    )

    results.append(
        (
            "Unit Deletion",
            ok
        )
    )


    # ========================================================
    # Negative: Object Type
    # ========================================================

    section(
        "Structural Mutation: Object Type"
    )

    mutated = mutate_object_type(
        world
    )

    ok = compare_non_equivalent(
        "Object Type Mutation",
        world,
        mutated
    )

    results.append(
        (
            "Object Type Mutation",
            ok
        )
    )


    # ========================================================
    # Summary
    # ========================================================

    print()
    print("=" * 60)
    print(
        "Struct3D v3.1"
    )
    print("=" * 60)

    passed = 0

    for name, ok in results:

        print(
            "{:<48} {}".format(
                name + ":",
                "PASS"
                if ok
                else "FAIL"
            )
        )

        if ok:

            passed += 1

    total = len(
        results
    )

    failed = total - passed

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

    if failed == 0:

        print(
            "STATUS: PASS"
        )

    else:

        print(
            "STATUS: FAIL"
        )

    print(
        "=" * 60
    )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    main()