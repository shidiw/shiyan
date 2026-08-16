# ============================================================
# Struct3D v3.4
# experiments/v34/run_v34_structural_automorphism.py
#
# Structural Automorphism Regression Suite
#
# Core principle
# ------------------------------------------------------------
#
# A structural automorphism is a structure-preserving bijection
#
#       phi : W -> W
#
# such that
#
#       phi(W) ~= W
#
# and, because the domain and codomain are the same world,
#
#       phi(W) = W
#
# at the structural level.
#
# v3.4 extends v3.3 with:
#
#     Identity automorphism
#     Unit automorphism
#     Object automorphism
#     Instance automorphism
#     Relation automorphism
#     Combined hierarchical automorphism
#     Automorphism + rigid transform
#     Automorphism closure
#     Automorphism inverse
#     Automorphism composition
#
# Negative tests:
#
#     Primitive mutation
#     Object composition mutation
#     Relation type mutation
#
# CPU only
# ============================================================

from __future__ import annotations

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

VERSION = "3.4"
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

    return Rz @ Ry @ Rx


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
# Base World
# ============================================================

def build_base_world():

    world = WorldState()

    # --------------------------------------------------------
    # Four units.
    #
    # U0 and U1 are structurally identical.
    # U2 and U3 are structurally identical.
    #
    # This gives us non-trivial automorphisms.
    # --------------------------------------------------------

    unit_specs = [

        {
            "id": 0,
            "center": [0.0, 0.0, 0.0],
            "radius": 1.0,
            "seed": 10,
            "energy": 0.1
        },

        {
            "id": 1,
            "center": [3.0, 0.0, 0.0],
            "radius": 1.0,
            "seed": 10,
            "energy": 0.1
        },

        {
            "id": 2,
            "center": [8.0, 0.0, 0.0],
            "radius": 0.8,
            "seed": 20,
            "energy": 0.2
        },

        {
            "id": 3,
            "center": [10.5, 0.0, 0.0],
            "radius": 0.8,
            "seed": 20,
            "energy": 0.2
        }
    ]

    for spec in unit_specs:

        points = make_sphere(
            center=spec["center"],
            radius=spec["radius"],
            n=100,
            seed=spec["seed"]
        )

        world.add_unit({

            "id": spec["id"],

            "points": points,

            "primitive": "sphere",

            "parameters": {
                "radius": spec["radius"]
            },

            "energy": {
                "value": spec["energy"]
            }

        })

    # --------------------------------------------------------
    # Objects
    #
    # O0 = U0,U1
    # O1 = U2,U3
    #
    # Both objects have identical internal structure.
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

        "type": "assembly",

        "parts": [2, 3],

        "relations": [

            {
                "source": 2,
                "target": 3,
                "type": "connected"
            }

        ]

    })

    # --------------------------------------------------------
    # Instances
    #
    # I0 -> O0
    # I1 -> O1
    #
    # They have identical structural form.
    # --------------------------------------------------------

    world.add_instance({

        "id": 0,

        "object": 0,

        "parts": [0, 1]

    })

    world.add_instance({

        "id": 1,

        "object": 1,

        "parts": [2, 3]

    })

    # --------------------------------------------------------
    # World relations
    #
    # O0 <-> O1
    #
    # We use a symmetric pair so object swapping preserves
    # the relation structure.
    # --------------------------------------------------------

    world.add_relation({

        "source": 0,

        "target": 1,

        "type": "connected",

        "confidence": 1.0

    })

    world.add_relation({

        "source": 1,

        "target": 0,

        "type": "connected",

        "confidence": 1.0

    })

    return world


# ============================================================
# Identity Mapping
# ============================================================

def identity_mapping(world):

    return {

        "units": {
            int(k): int(k)
            for k in world.units.keys()
        },

        "objects": {
            int(k): int(k)
            for k in world.objects.keys()
        },

        "instances": {
            int(k): int(k)
            for k in world.instances.keys()
        },

        "relations": {
            int(i): int(i)
            for i in range(
                len(world.relations)
            )
        }
    }


# ============================================================
# Mapping Validation
# ============================================================

def validate_bijection(mapping):

    for category in (
        "units",
        "objects",
        "instances",
        "relations"
    ):

        values = list(
            mapping[category].values()
        )

        if len(values) != len(
            set(values)
        ):
            return False

    return True


# ============================================================
# Unit Mapping
# ============================================================

def automorphism_unit_swap(world):

    mapping = identity_mapping(
        world
    )

    mapping["units"] = {
        0: 1,
        1: 0,
        2: 3,
        3: 2
    }

    return mapping


# ============================================================
# Object Mapping
# ============================================================

def automorphism_object_swap(world):

    mapping = identity_mapping(
        world
    )

    mapping["objects"] = {
        0: 1,
        1: 0
    }

    return mapping


# ============================================================
# Instance Mapping
# ============================================================

def automorphism_instance_swap(world):

    mapping = identity_mapping(
        world
    )

    mapping["instances"] = {
        0: 1,
        1: 0
    }

    return mapping


# ============================================================
# Relation Mapping
# ============================================================

def automorphism_relation_swap(world):

    mapping = identity_mapping(
        world
    )

    mapping["relations"] = {
        0: 1,
        1: 0
    }

    return mapping


# ============================================================
# Combined Mapping
# ============================================================

def combined_automorphism(world):

    return {

        "units": {
            0: 1,
            1: 0,
            2: 3,
            3: 2
        },

        "objects": {
            0: 1,
            1: 0
        },

        "instances": {
            0: 1,
            1: 0
        },

        "relations": {
            0: 1,
            1: 0
        }
    }


# ============================================================
# Apply Automorphism
# ============================================================

def apply_automorphism(
    world,
    mapping
):

    if not validate_bijection(
        mapping
    ):
        raise ValueError(
            "Automorphism mapping must be bijective"
        )

    source = deep_copy_world(
        world
    )

    result = WorldState()

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    for old_id, unit in source.units.items():

        new_id = mapping[
            "units"
        ][
            int(old_id)
        ]

        new_unit = copy.deepcopy(
            unit
        )

        new_unit["id"] = new_id

        result.add_unit(
            new_unit
        )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    for old_id, obj in source.objects.items():

        new_id = mapping[
            "objects"
        ][
            int(old_id)
        ]

        new_obj = copy.deepcopy(
            obj
        )

        new_obj["id"] = new_id

        # Remap unit references.
        if "parts" in new_obj:

            new_obj["parts"] = [

                mapping[
                    "units"
                ][
                    int(unit_id)
                ]

                for unit_id
                in new_obj["parts"]

            ]

        # Remap internal unit relations.
        if "relations" in new_obj:

            for relation in new_obj["relations"]:

                if "source" in relation:

                    relation["source"] = mapping[
                        "units"
                    ][
                        int(relation["source"])
                    ]

                if "target" in relation:

                    relation["target"] = mapping[
                        "units"
                    ][
                        int(relation["target"])
                    ]

        result.add_object(
            new_obj
        )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    for old_id, instance in source.instances.items():

        new_id = mapping[
            "instances"
        ][
            int(old_id)
        ]

        new_instance = copy.deepcopy(
            instance
        )

        new_instance["id"] = new_id

        if "object" in new_instance:

            new_instance["object"] = mapping[
                "objects"
            ][
                int(new_instance["object"])
            ]

        if "parts" in new_instance:

            new_instance["parts"] = [

                mapping[
                    "units"
                ][
                    int(unit_id)
                ]

                for unit_id
                in new_instance["parts"]

            ]

        result.add_instance(
            new_instance
        )

    # --------------------------------------------------------
    # World Relations
    # --------------------------------------------------------

    relation_records = [

        None
        for _ in source.relations
    ]

    for old_relation_id, relation in enumerate(
        source.relations
    ):

        new_relation_id = mapping[
            "relations"
        ][
            int(old_relation_id)
        ]

        new_relation = copy.deepcopy(
            relation
        )

        if "source" in new_relation:

            new_relation["source"] = mapping[
                "objects"
            ][
                int(new_relation["source"])
            ]

        if "target" in new_relation:

            new_relation["target"] = mapping[
                "objects"
            ][
                int(new_relation["target"])
            ]

        relation_records[
            new_relation_id
        ] = new_relation

    for relation in relation_records:

        result.add_relation(
            relation
        )

    return result


# ============================================================
# Composition of Mappings
# ============================================================

def compose_mappings(
    psi,
    phi
):
    """
    Return psi o phi.

    First apply phi.
    Then apply psi.

        (psi o phi)(x) = psi(phi(x))
    """

    result = {}

    for category in (
        "units",
        "objects",
        "instances",
        "relations"
    ):

        result[category] = {}

        for source, middle in phi[
            category
        ].items():

            result[category][
                int(source)
            ] = psi[
                category
            ][
                int(middle)
            ]

    return result


# ============================================================
# Inverse Mapping
# ============================================================

def inverse_mapping(
    mapping
):

    result = {}

    for category in (
        "units",
        "objects",
        "instances",
        "relations"
    ):

        result[category] = {}

        for source, target in mapping[
            category
        ].items():

            result[category][
                int(target)
            ] = int(source)

    return result


# ============================================================
# Mapping Equality
# ============================================================

def mapping_equal(
    mapping_a,
    mapping_b
):

    return mapping_a == mapping_b


# ============================================================
# Automorphism Check
# ============================================================

def is_automorphism(
    world,
    mapping,
    verbose=False
):

    if not validate_bijection(
        mapping
    ):
        return False

    transformed = apply_automorphism(
        world,
        mapping
    )

    sig_a = canonical_payload(
        world
    )

    sig_b = canonical_payload(
        transformed
    )

    equal = (
        sig_a == sig_b
    )

    if verbose:

        print(
            "Canonical structural equality:",
            equal
        )

        print(
            "Hash equality:",
            canonical_hash(world)
            ==
            canonical_hash(transformed)
        )

    return equal


# ============================================================
# Rigid Transform
# ============================================================

def rigid_transform_world(
    world,
    R,
    t
):

    result = deep_copy_world(
        world
    )

    for unit in result.units.values():

        points = np.asarray(
            unit["points"],
            dtype=float
        )

        unit["points"] = transform_points(
            points,
            R,
            t
        )

    return result


# ============================================================
# Validation
# ============================================================

def test_validation(world):

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
# Positive Automorphism Test
# ============================================================

def test_automorphism(
    name,
    world,
    mapping
):

    print()
    print(name)

    print(
        "Mapping:"
    )

    for category in (
        "units",
        "objects",
        "instances",
        "relations"
    ):

        print(
            "  {}: {}".format(
                category,
                mapping[category]
            )
        )

    transformed = apply_automorphism(
        world,
        mapping
    )

    canonical_equal = (
        canonical_payload(world)
        ==
        canonical_payload(transformed)
    )

    hash_equal = (
        canonical_hash(world)
        ==
        canonical_hash(transformed)
    )

    automorphism = (
        canonical_equal
        and
        hash_equal
    )

    print(
        "Canonical structural equality:",
        canonical_equal
    )

    print(
        "Hash equality:",
        hash_equal
    )

    print(
        "Automorphism:",
        automorphism
    )

    passed = automorphism

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
# Negative Test
# ============================================================

def test_non_automorphism(
    name,
    world,
    candidate
):

    print()
    print(name)

    canonical_equal = (
        canonical_payload(world)
        ==
        canonical_payload(candidate)
    )

    hash_equal = (
        canonical_hash(world)
        ==
        canonical_hash(candidate)
    )

    automorphism = (
        canonical_equal
        and
        hash_equal
    )

    print(
        "Canonical structural equality:",
        canonical_equal
    )

    print(
        "Hash equality:",
        hash_equal
    )

    print(
        "Automorphism:",
        automorphism
    )

    passed = not automorphism

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
# Structural Mutations
# ============================================================

def mutate_primitive(world):

    result = deep_copy_world(
        world
    )

    result.units[
        0
    ][
        "primitive"
    ] = "cube"

    return result


def mutate_object_composition(world):

    result = deep_copy_world(
        world
    )

    result.objects[
        0
    ][
        "parts"
    ] = [0]

    return result


def mutate_relation_type(world):

    result = deep_copy_world(
        world
    )

    result.relations[
        0
    ][
        "type"
    ] = "contact"

    return result


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v3.4 Structural Automorphism Regression Suite"
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

    print(
        "Units:",
        len(world.units)
    )

    print(
        "Objects:",
        len(world.objects)
    )

    print(
        "Instances:",
        len(world.instances)
    )

    print(
        "Relations:",
        len(world.relations)
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
    # Reflexive
    # ========================================================

    section(
        "Reflexive Automorphism"
    )

    identity = identity_mapping(
        world
    )

    ok = test_automorphism(
        "Identity Automorphism",
        world,
        identity
    )

    results.append(
        (
            "Identity Automorphism",
            ok
        )
    )

    # ========================================================
    # Unit
    # ========================================================

    section(
        "Unit Automorphism"
    )

    unit_mapping = automorphism_unit_swap(
        world
    )

    ok = test_automorphism(
        "Unit Automorphism",
        world,
        unit_mapping
    )

    results.append(
        (
            "Unit Automorphism",
            ok
        )
    )

    # ========================================================
    # Object
    # ========================================================

    section(
        "Object Automorphism"
    )

    object_mapping = automorphism_object_swap(
        world
    )

    ok = test_automorphism(
        "Object Automorphism",
        world,
        object_mapping
    )

    results.append(
        (
            "Object Automorphism",
            ok
        )
    )

    # ========================================================
    # Instance
    # ========================================================

    section(
        "Instance Automorphism"
    )

    instance_mapping = automorphism_instance_swap(
        world
    )

    ok = test_automorphism(
        "Instance Automorphism",
        world,
        instance_mapping
    )

    results.append(
        (
            "Instance Automorphism",
            ok
        )
    )

    # ========================================================
    # Relation
    # ========================================================

    section(
        "Relation Automorphism"
    )

    relation_mapping = automorphism_relation_swap(
        world
    )

    ok = test_automorphism(
        "Relation Automorphism",
        world,
        relation_mapping
    )

    results.append(
        (
            "Relation Automorphism",
            ok
        )
    )

    # ========================================================
    # Combined
    # ========================================================

    section(
        "Combined Structural Automorphism"
    )

    combined = combined_automorphism(
        world
    )

    ok = test_automorphism(
        "Combined Structural Automorphism",
        world,
        combined
    )

    results.append(
        (
            "Combined Structural Automorphism",
            ok
        )
    )

    # ========================================================
    # Combined + rigid
    # ========================================================

    section(
        "Automorphism + Rigid Transform"
    )

    R = random_rotation(
        rng
    )

    t = rng.uniform(
        -100.0,
        100.0,
        size=3
    )

    transformed_world = rigid_transform_world(
        world,
        R,
        t
    )

    transformed_then_automorphism = (
        apply_automorphism(
            transformed_world,
            combined
        )
    )

    canonical_equal = (
        canonical_payload(
            world
        )
        ==
        canonical_payload(
            transformed_then_automorphism
        )
    )

    hash_equal = (
        canonical_hash(
            world
        )
        ==
        canonical_hash(
            transformed_then_automorphism
        )
    )

    ok = (
        canonical_equal
        and
        hash_equal
    )

    print(
        "Rigid rotation determinant:",
        "{:.12f}".format(
            np.linalg.det(R)
        )
    )

    print(
        "Rigid translation:",
        np.array2string(
            t,
            precision=6
        )
    )

    print(
        "Canonical structural equality:",
        canonical_equal
    )

    print(
        "Hash equality:",
        hash_equal
    )

    print(
        "Automorphism:",
        ok
    )

    print(
        "[{}] Automorphism + Rigid Transform".format(
            "PASS"
            if ok
            else "FAIL"
        )
    )

    results.append(
        (
            "Automorphism + Rigid Transform",
            ok
        )
    )

    # ========================================================
    # Closure
    # ========================================================

    section(
        "Automorphism Closure"
    )

    phi = unit_mapping

    psi = combined

    composed = compose_mappings(
        psi,
        phi
    )

    closure_ok = is_automorphism(
        world,
        composed
    )

    print(
        "phi:",
        phi
    )

    print(
        "psi:",
        psi
    )

    print(
        "psi o phi:",
        composed
    )

    print(
        "Closure:",
        closure_ok
    )

    print(
        "[{}] Automorphism Closure".format(
            "PASS"
            if closure_ok
            else "FAIL"
        )
    )

    results.append(
        (
            "Automorphism Closure",
            closure_ok
        )
    )

    # ========================================================
    # Inverse
    # ========================================================

    section(
        "Automorphism Inverse"
    )

    inverse = inverse_mapping(
        combined
    )

    identity_from_inverse = compose_mappings(
        inverse,
        combined
    )

    identity_expected = identity_mapping(
        world
    )

    inverse_ok = (
        mapping_equal(
            identity_from_inverse,
            identity_expected
        )
        and
        is_automorphism(
            world,
            inverse
        )
    )

    print(
        "phi:",
        combined
    )

    print(
        "phi^-1:",
        inverse
    )

    print(
        "phi^-1 o phi:",
        identity_from_inverse
    )

    print(
        "Inverse exists:",
        inverse_ok
    )

    print(
        "[{}] Automorphism Inverse".format(
            "PASS"
            if inverse_ok
            else "FAIL"
        )
    )

    results.append(
        (
            "Automorphism Inverse",
            inverse_ok
        )
    )

    # ========================================================
    # Composition
    # ========================================================

    section(
        "Automorphism Composition"
    )

    composition = compose_mappings(
        combined,
        combined
    )

    composition_ok = is_automorphism(
        world,
        composition
    )

    print(
        "phi o phi:",
        composition
    )

    print(
        "Composition preserves structure:",
        composition_ok
    )

    print(
        "[{}] Automorphism Composition".format(
            "PASS"
            if composition_ok
            else "FAIL"
        )
    )

    results.append(
        (
            "Automorphism Composition",
            composition_ok
        )
    )

    # ========================================================
    # Negative: primitive
    # ========================================================

    section(
        "Structural Non-Automorphism: Primitive"
    )

    candidate = mutate_primitive(
        world
    )

    ok = test_non_automorphism(
        "Primitive Mutation",
        world,
        candidate
    )

    results.append(
        (
            "Primitive Mutation",
            ok
        )
    )

    # ========================================================
    # Negative: object composition
    # ========================================================

    section(
        "Structural Non-Automorphism: Object Composition"
    )

    candidate = mutate_object_composition(
        world
    )

    ok = test_non_automorphism(
        "Object Composition Mutation",
        world,
        candidate
    )

    results.append(
        (
            "Object Composition Mutation",
            ok
        )
    )

    # ========================================================
    # Negative: relation type
    # ========================================================

    section(
        "Structural Non-Automorphism: Relation Type"
    )

    candidate = mutate_relation_type(
        world
    )

    ok = test_non_automorphism(
        "Relation Type Mutation",
        world,
        candidate
    )

    results.append(
        (
            "Relation Type Mutation",
            ok
        )
    )

    # ========================================================
    # Summary
    # ========================================================

    print()
    print("=" * 60)
    print(
        "Struct3D v3.4"
    )
    print("=" * 60)

    passed = 0

    for name, ok in results:

        print(
            "{:<52} {}".format(
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