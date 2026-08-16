# ============================================================
# Struct3D v3.2
# experiments/v32/run_v32_structural_equivalence.py
#
# Structural Equivalence Regression Suite
#
# Core principle
#
#     W1 ~Struct W2
#         =>
#     identical canonical representation
#
#     W1 not~Struct W2
#         =>
#     different canonical representation
#
# v3.2 extends v3.1 with:
#
#     Unit permutation
#     Object permutation
#     Instance permutation
#     Relation permutation
#     Combined hierarchical permutation
#     Combined permutation + rigid transform
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

VERSION = "3.2"
SEED = 20260814

# Maximum number of elements shown in a compact diff.
MAX_PREVIEW_ITEMS = 3

# Numerical tolerance used ONLY for diagnostic reporting.
# It does NOT change canonical equality.
DIFF_RTOL = 1e-8
DIFF_ATOL = 1e-10


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


# ============================================================
# Compact Representation Helpers
# ============================================================

def short_repr(value, max_items=MAX_PREVIEW_ITEMS):
    """
    Compact representation for terminal diagnostics.

    Prevents enormous point-cloud arrays / tuples from
    flooding the terminal.
    """

    if isinstance(value, np.ndarray):

        arr = np.asarray(value)

        flat = arr.reshape(-1)

        preview = flat[:max_items]

        return (
            "ndarray("
            f"shape={arr.shape}, "
            f"dtype={arr.dtype}, "
            f"preview={preview.tolist()}"
            + (
                ", ..."
                if flat.size > max_items
                else ""
            )
            + ")"
        )

    if isinstance(value, dict):

        keys = list(value.keys())

        preview_keys = keys[:max_items]

        return (
            "dict("
            f"keys={preview_keys}"
            + (
                ", ..."
                if len(keys) > max_items
                else ""
            )
            + ")"
        )

    if isinstance(value, (list, tuple)):

        length = len(value)

        preview = [
            short_repr(
                item,
                max_items=max_items
            )
            for item in value[:max_items]
        ]

        return (
            f"{type(value).__name__}("
            f"len={length}, "
            f"preview={preview}"
            + (
                ", ..."
                if length > max_items
                else ""
            )
            + ")"
        )

    return repr(value)


def compare_numeric_arrays(a, b):
    """
    Diagnostic comparison for numerical arrays.

    Returns:
        dict or None
    """

    if not isinstance(a, np.ndarray):
        return None

    if not isinstance(b, np.ndarray):
        return None

    if a.shape != b.shape:

        return {
            "kind": "shape_mismatch",
            "shape_a": a.shape,
            "shape_b": b.shape
        }

    if not (
        np.issubdtype(a.dtype, np.number)
        and
        np.issubdtype(b.dtype, np.number)
    ):
        return None

    a64 = np.asarray(
        a,
        dtype=np.float64
    )

    b64 = np.asarray(
        b,
        dtype=np.float64
    )

    diff = np.abs(
        a64 - b64
    )

    if diff.size == 0:

        return {
            "kind": "numeric",
            "max_abs": 0.0,
            "mean_abs": 0.0,
            "allclose": True
        }

    finite = np.isfinite(diff)

    if not np.all(finite):

        return {
            "kind": "numeric",
            "max_abs": float(
                np.nanmax(diff)
            ),
            "mean_abs": float(
                np.nanmean(diff)
            ),
            "allclose": False,
            "finite": False
        }

    max_abs = float(
        np.max(diff)
    )

    mean_abs = float(
        np.mean(diff)
    )

    allclose = bool(
        np.allclose(
            a64,
            b64,
            rtol=DIFF_RTOL,
            atol=DIFF_ATOL
        )
    )

    return {
        "kind": "numeric",
        "max_abs": max_abs,
        "mean_abs": mean_abs,
        "allclose": allclose,
        "finite": True
    }


def describe_difference(
    key,
    value_a,
    value_b
):
    """
    Compact structural difference reporter.
    """

    print()
    print(
        "DIFF KEY:",
        key
    )

    # --------------------------------------------------------
    # Numeric ndarray
    # --------------------------------------------------------

    numeric = compare_numeric_arrays(
        value_a,
        value_b
    )

    if numeric is not None:

        print(
            "Type:",
            "numpy.ndarray"
        )

        if numeric["kind"] == "shape_mismatch":

            print(
                "Shape A:",
                numeric["shape_a"]
            )

            print(
                "Shape B:",
                numeric["shape_b"]
            )

            return

        print(
            "Shape:",
            value_a.shape
        )

        print(
            "Dtype A:",
            value_a.dtype
        )

        print(
            "Dtype B:",
            value_b.dtype
        )

        print(
            "Max abs error:",
            "{:.12e}".format(
                numeric["max_abs"]
            )
        )

        print(
            "Mean abs error:",
            "{:.12e}".format(
                numeric["mean_abs"]
            )
        )

        print(
            "Allclose:",
            numeric["allclose"]
        )

        print(
            "A preview:",
            short_repr(value_a)
        )

        print(
            "B preview:",
            short_repr(value_b)
        )

        return

    # --------------------------------------------------------
    # Lists / tuples
    # --------------------------------------------------------

    if (
        isinstance(value_a, (list, tuple))
        and
        isinstance(value_b, (list, tuple))
    ):

        print(
            "Type A:",
            type(value_a).__name__
        )

        print(
            "Type B:",
            type(value_b).__name__
        )

        print(
            "Length A:",
            len(value_a)
        )

        print(
            "Length B:",
            len(value_b)
        )

        # Try element-wise inspection.
        limit = min(
            len(value_a),
            len(value_b)
        )

        found = False

        for i in range(limit):

            a_item = value_a[i]
            b_item = value_b[i]

            if a_item == b_item:
                continue

            found = True

            print()
            print(
                "First differing element:",
                i
            )

            print(
                "A:",
                short_repr(a_item)
            )

            print(
                "B:",
                short_repr(b_item)
            )

            # Nested numerical arrays.
            nested = compare_numeric_arrays(
                a_item,
                b_item
            )

            if nested is not None:

                print(
                    "Nested numeric diagnostic:",
                    nested
                )

            break

        if not found:

            if len(value_a) != len(value_b):

                print(
                    "Common prefix identical; "
                    "length differs."
                )

            else:

                print(
                    "Values differ in nested representation."
                )

        return

    # --------------------------------------------------------
    # Dictionaries
    # --------------------------------------------------------

    if (
        isinstance(value_a, dict)
        and
        isinstance(value_b, dict)
    ):

        keys = sorted(
            set(value_a.keys())
            |
            set(value_b.keys()),
            key=str
        )

        print(
            "Dictionary keys:",
            keys
        )

        for nested_key in keys:

            a_item = value_a.get(
                nested_key,
                "<MISSING>"
            )

            b_item = value_b.get(
                nested_key,
                "<MISSING>"
            )

            if a_item == b_item:
                continue

            print()
            print(
                "Nested differing key:",
                nested_key
            )

            print(
                "A:",
                short_repr(a_item)
            )

            print(
                "B:",
                short_repr(b_item)
            )

            nested = compare_numeric_arrays(
                a_item,
                b_item
            )

            if nested is not None:

                print(
                    "Numeric diagnostic:",
                    nested
                )

        return

    # --------------------------------------------------------
    # Generic
    # --------------------------------------------------------

    print(
        "Type A:",
        type(value_a)
    )

    print(
        "Type B:",
        type(value_b)
    )

    print(
        "A:",
        short_repr(value_a)
    )

    print(
        "B:",
        short_repr(value_b)
    )


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

    transformed = (
        X @ R.T
        +
        center
        +
        np.asarray(
            t,
            dtype=float
        )
    )

    return transformed


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
    # Units
    # --------------------------------------------------------

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

        points = make_sphere(
            center=centers[i],
            radius=radii[i],
            n=100,
            seed=10 * (i + 1)
        )

        world.add_unit({

            "id": i,

            "points": points,

            "primitive": "sphere",

            "parameters": {
                "radius": radii[i]
            },

            "energy": {
                "value": 0.1 + 0.1 * i
            }

        })

    # --------------------------------------------------------
    # Objects
    #
    # O0 = U0,U1
    # O1 = U2
    # O2 = U3,U4
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
    # World Relations
    #
    # Object 0 -> Object 1
    # Object 1 -> Object 2
    # Object 0 -> Object 2
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
# Comparison
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

    if not passed:

        print()
        print(
            "******** CANONICAL PAYLOAD DIFF ********"
        )

        payload_a = canonical_payload(
            world_a
        )

        payload_b = canonical_payload(
            world_b
        )

        print(
            "Payload A type:",
            type(payload_a)
        )

        print(
            "Payload B type:",
            type(payload_b)
        )

        # ----------------------------------------------------
        # Dictionary payload
        # ----------------------------------------------------

        if (
            isinstance(payload_a, dict)
            and
            isinstance(payload_b, dict)
        ):

            keys = sorted(
                set(payload_a.keys())
                |
                set(payload_b.keys()),
                key=str
            )

            diff_count = 0

            for key in keys:

                value_a = payload_a.get(
                    key,
                    "<MISSING>"
                )

                value_b = payload_b.get(
                    key,
                    "<MISSING>"
                )

                try:

                    equal = (
                        value_a == value_b
                    )

                    if isinstance(
                        equal,
                        np.ndarray
                    ):

                        equal = bool(
                            np.all(equal)
                        )

                except Exception:

                    equal = False

                if equal:
                    continue

                diff_count += 1

                describe_difference(
                    key,
                    value_a,
                    value_b
                )

                # Do not flood the terminal.
                if diff_count >= 5:

                    remaining = len(keys) - (
                        keys.index(key) + 1
                    )

                    if remaining > 0:

                        print()
                        print(
                            "... {} additional "
                            "top-level differences omitted."
                            .format(
                                remaining
                            )
                        )

                    break

        else:

            describe_difference(
                "ROOT",
                payload_a,
                payload_b
            )

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


def compare_non_equivalent(
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

    old_units = list(
        source.units.values()
    )

    old_to_new = {}

    for new_id, old_id in enumerate(
        permutation
    ):

        old_to_new[
            int(old_id)
        ] = int(new_id)

        unit = copy.deepcopy(
            old_units[old_id]
        )

        unit["id"] = new_id

        result.add_unit(
            unit
        )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    for object_id, obj in source.objects.items():

        new_obj = copy.deepcopy(
            obj
        )

        new_obj["parts"] = [

            old_to_new[
                int(unit_id)
            ]

            for unit_id
            in obj.get("parts", [])

        ]

        if "relations" in new_obj:

            for relation in new_obj["relations"]:

                if "source" in relation:

                    relation["source"] = old_to_new[
                        int(relation["source"])
                    ]

                if "target" in relation:

                    relation["target"] = old_to_new[
                        int(relation["target"])
                    ]

        result.add_object(
            new_obj
        )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    for instance_id, instance in source.instances.items():

        new_instance = copy.deepcopy(
            instance
        )

        if "parts" in new_instance:

            new_instance["parts"] = [

                old_to_new[
                    int(unit_id)
                ]

                for unit_id
                in new_instance["parts"]

            ]

        result.add_instance(
            new_instance
        )

    # --------------------------------------------------------
    # World relations
    #
    # World relations refer to OBJECT IDs,
    # not UNIT IDs.
    # --------------------------------------------------------

    for relation in source.relations:

        result.add_relation(
            copy.deepcopy(
                relation
            )
        )

    return result


# ============================================================
# Object Permutation
# ============================================================

def permute_objects(
    world,
    permutation
):

    source = deep_copy_world(
        world
    )

    result = WorldState()

    old_to_new = {}

    for new_id, old_id in enumerate(
        permutation
    ):

        old_to_new[
            int(old_id)
        ] = int(new_id)

    # --------------------------------------------------------
    # Units unchanged
    # --------------------------------------------------------

    for unit_id, unit in source.units.items():

        result.add_unit(
            copy.deepcopy(unit)
        )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    old_objects = list(
        source.objects.values()
    )

    for new_id, old_id in enumerate(
        permutation
    ):

        obj = copy.deepcopy(
            old_objects[old_id]
        )

        obj["id"] = new_id

        result.add_object(
            obj
        )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    for instance_id, instance in source.instances.items():

        new_instance = copy.deepcopy(
            instance
        )

        if "object" in new_instance:

            new_instance["object"] = old_to_new[
                int(new_instance["object"])
            ]

        result.add_instance(
            new_instance
        )

    # --------------------------------------------------------
    # World relations
    # --------------------------------------------------------

    for relation in source.relations:

        r = copy.deepcopy(
            relation
        )

        if "source" in r:

            r["source"] = old_to_new[
                int(r["source"])
            ]

        if "target" in r:

            r["target"] = old_to_new[
                int(r["target"])
            ]

        result.add_relation(
            r
        )

    return result


# ============================================================
# Instance Permutation
# ============================================================

def permute_instances(
    world,
    permutation
):

    source = deep_copy_world(
        world
    )

    result = WorldState()

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    for unit in source.units.values():

        result.add_unit(
            copy.deepcopy(unit)
        )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    for obj in source.objects.values():

        result.add_object(
            copy.deepcopy(obj)
        )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    old_instances = list(
        source.instances.values()
    )

    for new_id, old_id in enumerate(
        permutation
    ):

        instance = copy.deepcopy(
            old_instances[old_id]
        )

        instance["id"] = new_id

        result.add_instance(
            instance
        )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

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

        copy.deepcopy(
            relation
        )

        for relation
        in result.relations

    ]

    result.relations = [

        relations[i]

        for i in permutation

    ]

    return result


# ============================================================
# Dictionary Order
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
# Combined Hierarchical Permutation
# ============================================================

def combined_hierarchical_permutation(
    world,
    unit_perm,
    object_perm,
    instance_perm,
    relation_perm
):

    result = permute_units(
        world,
        unit_perm
    )

    result = permute_objects(
        result,
        object_perm
    )

    result = permute_instances(
        result,
        instance_perm
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
# Structural Mutations
# ============================================================

def mutate_primitive(world):

    result = deep_copy_world(
        world
    )

    result.units[
        0
    ]["primitive"] = "cube"

    return result


def mutate_object_composition(world):

    result = deep_copy_world(
        world
    )

    result.objects[
        0
    ]["parts"] = [0]

    return result


def mutate_instance_composition(world):

    result = deep_copy_world(
        world
    )

    result.instances[
        0
    ]["parts"] = [0]

    return result


def mutate_relation_type(world):

    result = deep_copy_world(
        world
    )

    result.relations[
        0
    ]["type"] = "contact"

    return result


def mutate_relation_confidence(world):

    result = deep_copy_world(
        world
    )

    result.relations[
        0
    ]["confidence"] = 0.25

    return result


def delete_relation(world):

    result = deep_copy_world(
        world
    )

    result.relations = result.relations[:-1]

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
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v3.2 Structural Equivalence Regression Suite"
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

    stats = world.canonical_statistics()

    print(
        "Canonical Statistics:",
        stats
    )

    print(
        "Canonical Hash:",
        canonical_hash(world)
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
    # Identity sanity
    # ========================================================

    section(
        "Canonical Identity Sanity"
    )

    signature = canonical_signature(
        world
    )

    pickle_safe = True

    try:

        pickle.dumps(
            canonical_payload(world),
            protocol=4
        )

    except Exception:

        pickle_safe = False

    ok = (
        signature is not None
        and
        pickle_safe
    )

    print(
        "Signature exists:",
        signature is not None
    )

    print(
        "Canonical payload pickle-safe:",
        pickle_safe
    )

    print(
        "[{}] Canonical Identity Sanity".format(
            "PASS" if ok else "FAIL"
        )
    )

    results.append(
        (
            "Canonical Identity Sanity",
            ok
        )
    )

    # ========================================================
    # Unit permutation
    # ========================================================

    section(
        "Unit Structural Equivalence"
    )

    unit_perm = rng.permutation(
        len(world.units)
    ).tolist()

    print(
        "Unit permutation:",
        unit_perm
    )

    candidate = permute_units(
        world,
        unit_perm
    )

    ok = compare_equivalent(
        "Unit Structural Equivalence",
        world,
        candidate
    )

    results.append(
        (
            "Unit Structural Equivalence",
            ok
        )
    )

    # ========================================================
    # Object permutation
    # ========================================================

    section(
        "Object Structural Equivalence"
    )

    object_perm = rng.permutation(
        len(world.objects)
    ).tolist()

    print(
        "Object permutation:",
        object_perm
    )

    candidate = permute_objects(
        world,
        object_perm
    )

    ok = compare_equivalent(
        "Object Structural Equivalence",
        world,
        candidate
    )

    results.append(
        (
            "Object Structural Equivalence",
            ok
        )
    )

    # ========================================================
    # Instance permutation
    # ========================================================

    section(
        "Instance Structural Equivalence"
    )

    instance_perm = rng.permutation(
        len(world.instances)
    ).tolist()

    print(
        "Instance permutation:",
        instance_perm
    )

    candidate = permute_instances(
        world,
        instance_perm
    )

    ok = compare_equivalent(
        "Instance Structural Equivalence",
        world,
        candidate
    )

    results.append(
        (
            "Instance Structural Equivalence",
            ok
        )
    )

    # ========================================================
    # Relation permutation
    # ========================================================

    section(
        "Relation Structural Equivalence"
    )

    relation_perm = rng.permutation(
        len(world.relations)
    ).tolist()

    print(
        "Relation permutation:",
        relation_perm
    )

    candidate = permute_relations(
        world,
        relation_perm
    )

    ok = compare_equivalent(
        "Relation Structural Equivalence",
        world,
        candidate
    )

    results.append(
        (
            "Relation Structural Equivalence",
            ok
        )
    )

    # ========================================================
    # Dictionary order
    # ========================================================

    section(
        "Dictionary Order Equivalence"
    )

    candidate = reverse_dictionary_order(
        world
    )

    ok = compare_equivalent(
        "Dictionary Order Equivalence",
        world,
        candidate
    )

    results.append(
        (
            "Dictionary Order Equivalence",
            ok
        )
    )

    # ========================================================
    # Combined hierarchy
    # ========================================================

    section(
        "Combined Hierarchical Structural Equivalence"
    )

    unit_perm = rng.permutation(
        len(world.units)
    ).tolist()

    object_perm = rng.permutation(
        len(world.objects)
    ).tolist()

    instance_perm = rng.permutation(
        len(world.instances)
    ).tolist()

    relation_perm = rng.permutation(
        len(world.relations)
    ).tolist()

    print(
        "Unit permutation:",
        unit_perm
    )

    print(
        "Object permutation:",
        object_perm
    )

    print(
        "Instance permutation:",
        instance_perm
    )

    print(
        "Relation permutation:",
        relation_perm
    )

    candidate = combined_hierarchical_permutation(
        world,
        unit_perm,
        object_perm,
        instance_perm,
        relation_perm
    )

    ok = compare_equivalent(
        "Combined Hierarchical Structural Equivalence",
        world,
        candidate
    )

    results.append(
        (
            "Combined Hierarchical Structural Equivalence",
            ok
        )
    )

    # ========================================================
    # Combined + rigid
    # ========================================================

    section(
        "Combined Structural Equivalence + Rigid Transform"
    )

    R = random_rotation(
        rng
    )

    t = rng.uniform(
        -100.0,
        100.0,
        size=3
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
            precision=6,
            suppress_small=False
        )
    )

    candidate = rigid_transform_world(
        candidate,
        R,
        t
    )

    ok = compare_equivalent(
        "Combined Structural Equivalence + Rigid Transform",
        world,
        candidate
    )

    results.append(
        (
            "Combined Structural Equivalence + Rigid Transform",
            ok
        )
    )

    # ========================================================
    # Negative: Primitive
    # ========================================================

    section(
        "Structural Non-Equivalence: Primitive"
    )

    candidate = mutate_primitive(
        world
    )

    ok = compare_non_equivalent(
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
    # Negative: Object composition
    # ========================================================

    section(
        "Structural Non-Equivalence: Object Composition"
    )

    candidate = mutate_object_composition(
        world
    )

    ok = compare_non_equivalent(
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
    # Negative: Instance composition
    # ========================================================

    section(
        "Structural Non-Equivalence: Instance Composition"
    )

    candidate = mutate_instance_composition(
        world
    )

    ok = compare_non_equivalent(
        "Instance Composition Mutation",
        world,
        candidate
    )

    results.append(
        (
            "Instance Composition Mutation",
            ok
        )
    )

    # ========================================================
    # Negative: Relation type
    # ========================================================

    section(
        "Structural Non-Equivalence: Relation Type"
    )

    candidate = mutate_relation_type(
        world
    )

    ok = compare_non_equivalent(
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
    # Negative: Relation confidence
    # ========================================================

    section(
        "Structural Non-Equivalence: Relation Confidence"
    )

    candidate = mutate_relation_confidence(
        world
    )

    ok = compare_non_equivalent(
        "Relation Confidence Mutation",
        world,
        candidate
    )

    results.append(
        (
            "Relation Confidence Mutation",
            ok
        )
    )

    # ========================================================
    # Negative: Relation deletion
    # ========================================================

    section(
        "Structural Non-Equivalence: Relation Deletion"
    )

    candidate = delete_relation(
        world
    )

    ok = compare_non_equivalent(
        "Relation Deletion",
        world,
        candidate
    )

    results.append(
        (
            "Relation Deletion",
            ok
        )
    )

    # ========================================================
    # Summary
    # ========================================================

    print()
    print("=" * 60)
    print(
        "Struct3D v3.2"
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