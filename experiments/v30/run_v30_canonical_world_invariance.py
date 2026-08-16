# ============================================================
# Struct3D v3.0
# experiments/v30/run_v30_canonical_world_invariance.py
#
# Canonical World Regression Suite
#
# Purpose:
#
#   Verify that the canonical structural world representation
#   is invariant to transformations that should not alter
#   structural identity.
#
# Tested invariances:
#
#   1. Base World
#   2. Validation
#   3. Translation
#   4. Rotation X
#   5. Rotation Y
#   6. Rotation Z
#   7. Multiple random rigid transforms
#   8. Unit permutation
#   9. Relation permutation
#  10. Entity insertion/order permutation
#  11. Combined permutation + rigid transform
#  12. Persistence round trip
#  13. Deterministic replay
#  14. Multi-replay hash stability
#
# Important:
#
#   This file intentionally does NOT modify the Struct3D
#   structural implementation.
#
#   It is a regression test for the existing canonical
#   world representation.
#
# CPU only.
# ============================================================

import os
import sys
import copy
import pickle
import hashlib

import numpy as np


# ============================================================
# Project Root
# ============================================================

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ============================================================
# World State
# ============================================================

try:

    from structure.world_state import WorldState

except ImportError:

    from structure.world_state import StructuralWorldState as WorldState


# ============================================================
# Constants
# ============================================================

VERSION = "3.0"

EPS = 1e-12

TEST_SEED = 20260814

PERSISTENCE_PATH = os.path.join(
    ROOT,
    "data",
    "world_state_v30_test.pkl"
)


# ============================================================
# Pretty Printing
# ============================================================

def print_header(title):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_section(title):

    print()
    print("-" * 60)
    print(title)
    print("-" * 60)


# ============================================================
# Rotation
# ============================================================

def rotation_matrix_x(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c]
        ],
        dtype=float
    )


def rotation_matrix_y(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c]
        ],
        dtype=float
    )


def rotation_matrix_z(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0]
        ],
        dtype=float
    )


def compose_rotation(
    rx,
    ry,
    rz
):

    return (
        rotation_matrix_z(rz)
        @
        rotation_matrix_y(ry)
        @
        rotation_matrix_x(rx)
    )


# ============================================================
# Rigid Transform
# ============================================================

def transform_points(
    points,
    R=None,
    t=None
):

    X = np.asarray(
        points,
        dtype=float
    )

    if R is None:

        R = np.eye(
            3,
            dtype=float
        )

    if t is None:

        t = np.zeros(
            3,
            dtype=float
        )

    R = np.asarray(
        R,
        dtype=float
    )

    t = np.asarray(
        t,
        dtype=float
    )

    return X @ R.T + t


# ============================================================
# Primitive Generation
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

    directions = rng.normal(
        size=(n, 3)
    )

    directions /= (
        np.linalg.norm(
            directions,
            axis=1,
            keepdims=True
        )
        +
        EPS
    )

    return (
        np.asarray(
            center,
            dtype=float
        )
        +
        radius
        *
        directions
    )


# ============================================================
# Base Scene
# ============================================================

def make_scene():

    points_list = [

        make_sphere(
            center=[0.0, 0.0, 0.0],
            radius=1.0,
            n=100,
            seed=10
        ),

        make_sphere(
            center=[2.2, 0.0, 0.0],
            radius=0.8,
            n=100,
            seed=20
        ),

        make_sphere(
            center=[4.4, 0.0, 0.0],
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
            center=[10.3, 0.0, 0.0],
            radius=0.8,
            n=100,
            seed=50
        )
    ]

    return points_list


# ============================================================
# Relations
# ============================================================

def make_relations():

    return [

        {
            "source": 0,
            "target": 1,
            "type": "connected",
            "confidence": 1.0
        },

        {
            "source": 1,
            "target": 2,
            "type": "connected",
            "confidence": 1.0
        },

        {
            "source": 3,
            "target": 4,
            "type": "connected",
            "confidence": 1.0
        }

    ]


# ============================================================
# World Construction
# ============================================================

def build_world(
    points_list,
    relations=None
):

    world = WorldState()

    if relations is None:

        relations = make_relations()

    # --------------------------------------------------------
    # Add Units
    # --------------------------------------------------------

    for i, points in enumerate(
        points_list
    ):

        record = {

            "id":
                i,

            "points":
                np.asarray(
                    points,
                    dtype=float
                ),

            "primitive":
                "sphere",

            "parameters":
                {
                    "radius":
                        float(
                            np.mean(
                                np.linalg.norm(
                                    points
                                    -
                                    np.mean(
                                        points,
                                        axis=0
                                    ),
                                    axis=1
                                )
                            )
                        )
                },

            "energy":
                {
                    "value":
                        0.1
                        +
                        0.1 * i
                }

        }

        # ----------------------------------------------------
        # Try canonical add API.
        # ----------------------------------------------------

        added = False

        if hasattr(
            world,
            "add_unit"
        ):

            try:

                world.add_unit(
                    record
                )

                added = True

            except TypeError:

                pass

            except Exception:

                pass

        # ----------------------------------------------------
        # Direct fallback.
        # ----------------------------------------------------

        if not added:

            world.units[
                i
            ] = record

    # --------------------------------------------------------
    # Objects
    #
    # For v3.0 canonical-world regression we intentionally
    # keep one object per unit.
    #
    # This isolates canonical-world invariance from assembly
    # policy and makes the regression suite deterministic.
    # --------------------------------------------------------

    for i in range(
        len(points_list)
    ):

        record = {

            "id":
                i,

            "parts":
                [i],

            "type":
                "single",

            "primitive":
                "sphere",

            "energy":
                0.1
                +
                0.1 * i

        }

        added = False

        if hasattr(
            world,
            "add_object"
        ):

            try:

                world.add_object(
                    record
                )

                added = True

            except TypeError:

                pass

            except Exception:

                pass

        if not added:

            world.objects[
                i
            ] = record

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    for i in range(
        len(points_list)
    ):

        record = {

            "id":
                i,

            "object":
                i,

            "points":
                np.asarray(
                    points_list[i],
                    dtype=float
                ),

            "primitive":
                "sphere"

        }

        added = False

        if hasattr(
            world,
            "add_instance"
        ):

            try:

                world.add_instance(
                    record
                )

                added = True

            except TypeError:

                pass

            except Exception:

                pass

        if not added:

            world.instances[
                i
            ] = record

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    for relation in relations:

        record = copy.deepcopy(
            relation
        )

        added = False

        if hasattr(
            world,
            "add_relation"
        ):

            try:

                world.add_relation(
                    record
                )

                added = True

            except TypeError:

                pass

            except Exception:

                pass

        if not added:

            world.relations.append(
                record
            )

    return world


# ============================================================
# Deep Copy
# ============================================================

def clone_world(
    world
):

    return copy.deepcopy(
        world
    )


# ============================================================
# Coordinate Transformation
# ============================================================

def transform_world_geometry(
    world,
    R=None,
    t=None
):

    result = clone_world(
        world
    )

    if R is None:

        R = np.eye(
            3,
            dtype=float
        )

    if t is None:

        t = np.zeros(
            3,
            dtype=float
        )

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    for unit in result.units.values():

        if not isinstance(
            unit,
            dict
        ):

            continue

        if "points" in unit:

            try:

                unit["points"] = transform_points(
                    unit["points"],
                    R,
                    t
                )

            except Exception:

                pass

        if "center" in unit:

            try:

                unit["center"] = transform_points(
                    np.asarray(
                        unit["center"],
                        dtype=float
                    ).reshape(
                        1,
                        3
                    ),
                    R,
                    t
                )[0]

            except Exception:

                pass

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    for obj in result.objects.values():

        if not isinstance(
            obj,
            dict
        ):

            continue

        if "center" in obj:

            try:

                obj["center"] = transform_points(
                    np.asarray(
                        obj["center"],
                        dtype=float
                    ).reshape(
                        1,
                        3
                    ),
                    R,
                    t
                )[0]

            except Exception:

                pass

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    for instance in result.instances.values():

        if not isinstance(
            instance,
            dict
        ):

            continue

        if "points" in instance:

            try:

                instance["points"] = transform_points(
                    instance["points"],
                    R,
                    t
                )

            except Exception:

                pass

        if "center" in instance:

            try:

                instance["center"] = transform_points(
                    np.asarray(
                        instance["center"],
                        dtype=float
                    ).reshape(
                        1,
                        3
                    ),
                    R,
                    t
                )[0]

            except Exception:

                pass

    return result


# ============================================================
# Unit Permutation
# ============================================================

def permute_units(
    world,
    permutation
):

    permutation = list(
        permutation
    )

    result = WorldState()

    old_units = world.units

    old_objects = world.objects

    old_instances = world.instances

    old_relations = world.relations

    # --------------------------------------------------------
    # Old unit -> new unit ID
    # --------------------------------------------------------

    old_to_new = {}

    for new_id, old_id in enumerate(
        permutation
    ):

        old_to_new[
            old_id
        ] = new_id

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    for new_id, old_id in enumerate(
        permutation
    ):

        record = copy.deepcopy(
            old_units[
                old_id
            ]
        )

        if isinstance(
            record,
            dict
        ):

            record["id"] = new_id

        result.units[
            new_id
        ] = record

    # --------------------------------------------------------
    # Objects
    #
    # Objects are kept structurally equivalent but remapped
    # according to the unit permutation.
    # --------------------------------------------------------

    object_records = []

    for old_object_id, obj in old_objects.items():

        record = copy.deepcopy(
            obj
        )

        if isinstance(
            record,
            dict
        ):

            parts = record.get(
                "parts",
                []
            )

            new_parts = []

            for part in parts:

                try:

                    old_unit_id = int(
                        part
                    )

                except Exception:

                    continue

                if old_unit_id in old_to_new:

                    new_parts.append(
                        old_to_new[
                            old_unit_id
                        ]
                    )

            record["parts"] = sorted(
                new_parts
            )

        object_records.append(
            (
                int(old_object_id),
                record
            )
        )

    for new_object_id, (
        old_object_id,
        record
    ) in enumerate(
        object_records
    ):

        if isinstance(
            record,
            dict
        ):

            record["id"] = new_object_id

        result.objects[
            new_object_id
        ] = record

    # --------------------------------------------------------
    # Old object -> new object
    # --------------------------------------------------------

    object_id_map = {}

    for new_id, (
        old_id,
        _
    ) in enumerate(
        object_records
    ):

        object_id_map[
            old_id
        ] = new_id

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    instance_records = []

    for old_instance_id, instance in old_instances.items():

        record = copy.deepcopy(
            instance
        )

        if isinstance(
            record,
            dict
        ):

            if "object" in record:

                try:

                    old_object_id = int(
                        record["object"]
                    )

                    if old_object_id in object_id_map:

                        record["object"] = (
                            object_id_map[
                                old_object_id
                            ]
                        )

                except Exception:

                    pass

        instance_records.append(
            (
                int(old_instance_id),
                record
            )
        )

    for new_instance_id, (
        old_instance_id,
        record
    ) in enumerate(
        instance_records
    ):

        if isinstance(
            record,
            dict
        ):

            record["id"] = new_instance_id

        result.instances[
            new_instance_id
        ] = record

    # --------------------------------------------------------
    # Relations
    #
    # Relations refer to object IDs in the canonical world.
    # --------------------------------------------------------

    for relation in old_relations:

        record = copy.deepcopy(
            relation
        )

        if not isinstance(
            record,
            dict
        ):

            continue

        if (
            "source" in record
            and
            "target" in record
        ):

            try:

                old_source = int(
                    record["source"]
                )

                old_target = int(
                    record["target"]
                )

                if (
                    old_source in object_id_map
                    and
                    old_target in object_id_map
                ):

                    record["source"] = (
                        object_id_map[
                            old_source
                        ]
                    )

                    record["target"] = (
                        object_id_map[
                            old_target
                        ]
                    )

            except Exception:

                pass

        result.relations.append(
            record
        )

    return result


# ============================================================
# Relation Permutation
# ============================================================

def permute_relations(
    world,
    permutation
):

    result = clone_world(
        world
    )

    relations = [
        copy.deepcopy(
            world.relations[i]
        )
        for i in permutation
    ]

    result.relations = relations

    return result


# ============================================================
# Entity Order Permutation
# ============================================================

def permute_entity_order(
    world,
    unit_permutation,
    relation_permutation
):

    result = permute_units(
        world,
        unit_permutation
    )

    result = permute_relations(
        result,
        relation_permutation
    )

    return result


# ============================================================
# Canonical Signature
# ============================================================

def canonical_signature(
    world
):

    if not hasattr(
        world,
        "canonical_signature"
    ):

        raise RuntimeError(
            "WorldState does not expose "
            "canonical_signature()."
        )

    return world.canonical_signature()


# ============================================================
# Canonical Payload
# ============================================================

def canonical_payload(
    world
):

    if hasattr(
        world,
        "canonical_payload"
    ):

        return world.canonical_payload()

    return canonical_signature(
        world
    )


# ============================================================
# Canonical Hash
# ============================================================

def canonical_hash(
    world
):

    payload = canonical_payload(
        world
    )

    data = pickle.dumps(
        payload,
        protocol=4
    )

    return hashlib.sha256(
        data
    ).hexdigest()


# ============================================================
# Canonical Statistics
# ============================================================

def canonical_statistics(
    world
):

    if hasattr(
        world,
        "canonical_statistics"
    ):

        return world.canonical_statistics()

    signature = canonical_signature(
        world
    )

    return {

        "units":
            len(
                signature.get(
                    "units",
                    []
                )
            ),

        "objects":
            len(
                signature.get(
                    "objects",
                    []
                )
            ),

        "instances":
            len(
                signature.get(
                    "instances",
                    []
                )
            ),

        "relations":
            len(
                signature.get(
                    "relations",
                    []
                )
            )
    }


# ============================================================
# Validation
# ============================================================

def validate_world(
    world
):

    if not hasattr(
        world,
        "validate"
    ):

        return True

    result = world.validate()

    if isinstance(
        result,
        dict
    ):

        return bool(
            result.get(
                "valid",
                False
            )
        )

    return bool(
        result
    )


# ============================================================
# Equality
# ============================================================

def canonical_equal(
    world_a,
    world_b
):

    return (
        canonical_signature(
            world_a
        )
        ==
        canonical_signature(
            world_b
        )
    )


def hash_equal(
    world_a,
    world_b
):

    return (
        canonical_hash(
            world_a
        )
        ==
        canonical_hash(
            world_b
        )
    )


# ============================================================
# Save
# ============================================================

def save_world(
    world,
    path
):

    os.makedirs(
        os.path.dirname(
            path
        ),
        exist_ok=True
    )

    # --------------------------------------------------------
    # Prefer native persistence if available.
    # --------------------------------------------------------

    if hasattr(
        world,
        "save"
    ):

        try:

            world.save(
                path
            )

            return

        except Exception:

            pass

    # --------------------------------------------------------
    # Generic pickle fallback.
    # --------------------------------------------------------

    with open(
        path,
        "wb"
    ) as f:

        pickle.dump(
            world,
            f,
            protocol=4
        )


# ============================================================
# Load
# ============================================================

def load_world(
    path
):

    # --------------------------------------------------------
    # Try native class loader.
    # --------------------------------------------------------

    if hasattr(
        WorldState,
        "load"
    ):

        try:

            return WorldState.load(
                path
            )

        except Exception:

            pass

    # --------------------------------------------------------
    # Generic pickle fallback.
    # --------------------------------------------------------

    with open(
        path,
        "rb"
    ) as f:

        return pickle.load(
            f
        )


# ============================================================
# Test Result
# ============================================================

class TestResult:

    def __init__(
        self,
        name,
        passed
    ):

        self.name = name

        self.passed = bool(
            passed
        )

    def __bool__(
        self
    ):

        return self.passed


# ============================================================
# Base World Test
# ============================================================

def test_base_world(
    world
):

    print_section(
        "[1] Base World"
    )

    stats = canonical_statistics(
        world
    )

    h = canonical_hash(
        world
    )

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
        h
    )

    passed = validate_world(
        world
    )

    print(
        "[{}] World Validation".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Base World",
        passed
    )


# ============================================================
# Generic Invariance Test
# ============================================================

def run_invariance_test(
    name,
    world_a,
    world_b
):

    print_section(
        name
    )

    equal = canonical_equal(
        world_a,
        world_b
    )

    same_hash = hash_equal(
        world_a,
        world_b
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash equal:",
        same_hash
    )

    passed = (
        equal
        and
        same_hash
    )

    print(
        "[{}] {}".format(
            "PASS"
            if passed
            else
            "FAIL",
            name
        )
    )

    return TestResult(
        name,
        passed
    )


# ============================================================
# Translation Test
# ============================================================

def test_translation(
    world
):

    translation = np.array(
        [
            17.5,
            -8.25,
            31.75
        ],
        dtype=float
    )

    transformed = transform_world_geometry(
        world,
        R=np.eye(
            3
        ),
        t=translation
    )

    return run_invariance_test(
        "Translation Invariance",
        world,
        transformed
    )


# ============================================================
# Rotation X
# ============================================================

def test_rotation_x(
    world
):

    R = rotation_matrix_x(
        np.deg2rad(
            37.0
        )
    )

    transformed = transform_world_geometry(
        world,
        R=R
    )

    return run_invariance_test(
        "Rotation X Invariance",
        world,
        transformed
    )


# ============================================================
# Rotation Y
# ============================================================

def test_rotation_y(
    world
):

    R = rotation_matrix_y(
        np.deg2rad(
            53.0
        )
    )

    transformed = transform_world_geometry(
        world,
        R=R
    )

    return run_invariance_test(
        "Rotation Y Invariance",
        world,
        transformed
    )


# ============================================================
# Rotation Z
# ============================================================

def test_rotation_z(
    world
):

    R = rotation_matrix_z(
        np.deg2rad(
            71.0
        )
    )

    transformed = transform_world_geometry(
        world,
        R=R
    )

    return run_invariance_test(
        "Rotation Z Invariance",
        world,
        transformed
    )


# ============================================================
# Multi Rigid Transform Test
# ============================================================

def test_random_rigid_transforms(
    world,
    count=20
):

    print_section(
        "Random Rigid Transform Invariance"
    )

    rng = np.random.default_rng(
        TEST_SEED
    )

    all_passed = True

    base_hash = canonical_hash(
        world
    )

    for i in range(
        count
    ):

        angles = rng.uniform(
            -np.pi,
            np.pi,
            size=3
        )

        translation = rng.uniform(
            -100.0,
            100.0,
            size=3
        )

        R = compose_rotation(
            angles[0],
            angles[1],
            angles[2]
        )

        transformed = transform_world_geometry(
            world,
            R=R,
            t=translation
        )

        equal = canonical_equal(
            world,
            transformed
        )

        same_hash = (
            canonical_hash(
                transformed
            )
            ==
            base_hash
        )

        passed = (
            equal
            and
            same_hash
        )

        print(
            "Transform {:02d}: {}".format(
                i + 1,
                "PASS"
                if passed
                else
                "FAIL"
            )
        )

        if not passed:

            all_passed = False

    print(
        "[{}] Random Rigid Transform Invariance".format(
            "PASS"
            if all_passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Random Rigid Transform Invariance",
        all_passed
    )


# ============================================================
# Unit Permutation
# ============================================================

def test_unit_permutation(
    world
):

    rng = np.random.default_rng(
        TEST_SEED + 1
    )

    n = len(
        world.units
    )

    permutation = rng.permutation(
        n
    ).tolist()

    transformed = permute_units(
        world,
        permutation
    )

    print_section(
        "Unit Permutation Invariance"
    )

    print(
        "Permutation:",
        permutation
    )

    equal = canonical_equal(
        world,
        transformed
    )

    same_hash = hash_equal(
        world,
        transformed
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash equal:",
        same_hash
    )

    passed = (
        equal
        and
        same_hash
    )

    print(
        "[{}] Unit Permutation Invariance".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Unit Permutation Invariance",
        passed
    )


# ============================================================
# Relation Permutation
# ============================================================

def test_relation_permutation(
    world
):

    rng = np.random.default_rng(
        TEST_SEED + 2
    )

    n = len(
        world.relations
    )

    permutation = rng.permutation(
        n
    ).tolist()

    transformed = permute_relations(
        world,
        permutation
    )

    print_section(
        "Relation Permutation Invariance"
    )

    print(
        "Permutation:",
        permutation
    )

    print(
        "Original relations:",
        world.relations
    )

    print(
        "Permuted relations:",
        transformed.relations
    )

    equal = canonical_equal(
        world,
        transformed
    )

    same_hash = hash_equal(
        world,
        transformed
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash equal:",
        same_hash
    )

    passed = (
        equal
        and
        same_hash
    )

    print(
        "[{}] Relation Permutation Invariance".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Relation Permutation Invariance",
        passed
    )


# ============================================================
# Entity Order Permutation
# ============================================================

def test_entity_order_permutation(
    world
):

    rng = np.random.default_rng(
        TEST_SEED + 3
    )

    unit_permutation = rng.permutation(
        len(
            world.units
        )
    ).tolist()

    relation_permutation = rng.permutation(
        len(
            world.relations
        )
    ).tolist()

    transformed = permute_entity_order(
        world,
        unit_permutation,
        relation_permutation
    )

    print_section(
        "Entity Order Permutation Invariance"
    )

    print(
        "Unit permutation:",
        unit_permutation
    )

    print(
        "Relation permutation:",
        relation_permutation
    )

    equal = canonical_equal(
        world,
        transformed
    )

    same_hash = hash_equal(
        world,
        transformed
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash equal:",
        same_hash
    )

    passed = (
        equal
        and
        same_hash
    )

    print(
        "[{}] Entity Order Permutation Invariance".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Entity Order Permutation Invariance",
        passed
    )


# ============================================================
# Combined Permutation + Rigid Transform
# ============================================================

def test_combined_permutation_rigid(
    world
):

    rng = np.random.default_rng(
        TEST_SEED + 4
    )

    permutation = rng.permutation(
        len(
            world.units
        )
    ).tolist()

    relation_permutation = rng.permutation(
        len(
            world.relations
        )
    ).tolist()

    permuted = permute_entity_order(
        world,
        permutation,
        relation_permutation
    )

    angles = rng.uniform(
        -np.pi,
        np.pi,
        size=3
    )

    translation = rng.uniform(
        -50.0,
        50.0,
        size=3
    )

    R = compose_rotation(
        angles[0],
        angles[1],
        angles[2]
    )

    transformed = transform_world_geometry(
        permuted,
        R=R,
        t=translation
    )

    print_section(
        "Combined Permutation + Rigid Transform"
    )

    print(
        "Unit permutation:",
        permutation
    )

    print(
        "Relation permutation:",
        relation_permutation
    )

    print(
        "Translation:",
        translation
    )

    print(
        "Canonical equal:",
        canonical_equal(
            world,
            transformed
        )
    )

    print(
        "Hash equal:",
        hash_equal(
            world,
            transformed
        )
    )

    passed = (
        canonical_equal(
            world,
            transformed
        )
        and
        hash_equal(
            world,
            transformed
        )
    )

    print(
        "[{}] Combined Permutation + Rigid Transform".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Combined Permutation + Rigid Transform",
        passed
    )


# ============================================================
# Persistence
# ============================================================

def test_persistence(
    world
):

    print_section(
        "Persistence Round Trip"
    )

    save_world(
        world,
        PERSISTENCE_PATH
    )

    loaded = load_world(
        PERSISTENCE_PATH
    )

    equal = canonical_equal(
        world,
        loaded
    )

    same_hash = hash_equal(
        world,
        loaded
    )

    print(
        "Path:",
        PERSISTENCE_PATH
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash equal:",
        same_hash
    )

    passed = (
        equal
        and
        same_hash
    )

    print(
        "[{}] Persistence Round Trip".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Persistence Round Trip",
        passed
    )


# ============================================================
# Deterministic Replay
# ============================================================

def test_deterministic_replay():

    world_a = build_world(
        make_scene(),
        make_relations()
    )

    world_b = build_world(
        make_scene(),
        make_relations()
    )

    equal = canonical_equal(
        world_a,
        world_b
    )

    same_hash = hash_equal(
        world_a,
        world_b
    )

    print_section(
        "Deterministic Replay"
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash equal:",
        same_hash
    )

    passed = (
        equal
        and
        same_hash
    )

    print(
        "[{}] Deterministic Replay".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Deterministic Replay",
        passed
    )


# ============================================================
# Multi Replay Stability
# ============================================================

def test_multi_replay_stability(
    count=20
):

    print_section(
        "Multi-Replay Stability"
    )

    reference = build_world(
        make_scene(),
        make_relations()
    )

    reference_hash = canonical_hash(
        reference
    )

    all_passed = True

    for i in range(
        count
    ):

        replay = build_world(
            make_scene(),
            make_relations()
        )

        current_hash = canonical_hash(
            replay
        )

        passed = (
            current_hash
            ==
            reference_hash
        )

        print(
            "Replay {:02d}: {}".format(
                i + 1,
                "PASS"
                if passed
                else
                "FAIL"
            )
        )

        if not passed:

            all_passed = False

    print(
        "Reference Hash:",
        reference_hash
    )

    print(
        "[{}] Multi-Replay Stability".format(
            "PASS"
            if all_passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Multi-Replay Stability",
        all_passed
    )


# ============================================================
# Canonical Signature Sanity
# ============================================================

def test_canonical_signature_sanity(
    world
):

    print_section(
        "Canonical Signature Sanity"
    )

    signature = canonical_signature(
        world
    )

    payload = canonical_payload(
        world
    )

    serializable = True

    try:

        pickle.dumps(
            payload,
            protocol=4
        )

    except Exception:

        serializable = False

    signature_not_empty = (
        signature is not None
    )

    print(
        "Signature exists:",
        signature_not_empty
    )

    print(
        "Canonical payload pickle-safe:",
        serializable
    )

    passed = (
        signature_not_empty
        and
        serializable
    )

    print(
        "[{}] Canonical Signature Sanity".format(
            "PASS"
            if passed
            else
            "FAIL"
        )
    )

    return TestResult(
        "Canonical Signature Sanity",
        passed
    )


# ============================================================
# Main
# ============================================================

def main():

    print_header(
        "Struct3D v3.0 Canonical World Regression Suite"
    )

    print(
        "Version:",
        VERSION
    )

    print(
        "Seed:",
        TEST_SEED
    )

    # --------------------------------------------------------
    # Base world
    # --------------------------------------------------------

    world = build_world(
        make_scene(),
        make_relations()
    )

    results = []

    # --------------------------------------------------------
    # 1. Base
    # --------------------------------------------------------

    results.append(
        test_base_world(
            world
        )
    )

    # --------------------------------------------------------
    # 2. Canonical sanity
    # --------------------------------------------------------

    results.append(
        test_canonical_signature_sanity(
            world
        )
    )

    # --------------------------------------------------------
    # 3. Translation
    # --------------------------------------------------------

    results.append(
        test_translation(
            world
        )
    )

    # --------------------------------------------------------
    # 4. Rotation X
    # --------------------------------------------------------

    results.append(
        test_rotation_x(
            world
        )
    )

    # --------------------------------------------------------
    # 5. Rotation Y
    # --------------------------------------------------------

    results.append(
        test_rotation_y(
            world
        )
    )

    # --------------------------------------------------------
    # 6. Rotation Z
    # --------------------------------------------------------

    results.append(
        test_rotation_z(
            world
        )
    )

    # --------------------------------------------------------
    # 7. Random rigid transforms
    # --------------------------------------------------------

    results.append(
        test_random_rigid_transforms(
            world,
            count=20
        )
    )

    # --------------------------------------------------------
    # 8. Unit permutation
    # --------------------------------------------------------

    results.append(
        test_unit_permutation(
            world
        )
    )

    # --------------------------------------------------------
    # 9. Relation permutation
    # --------------------------------------------------------

    results.append(
        test_relation_permutation(
            world
        )
    )

    # --------------------------------------------------------
    # 10. Entity order permutation
    # --------------------------------------------------------

    results.append(
        test_entity_order_permutation(
            world
        )
    )

    # --------------------------------------------------------
    # 11. Combined permutation + rigid
    # --------------------------------------------------------

    results.append(
        test_combined_permutation_rigid(
            world
        )
    )

    # --------------------------------------------------------
    # 12. Persistence
    # --------------------------------------------------------

    results.append(
        test_persistence(
            world
        )
    )

    # --------------------------------------------------------
    # 13. Deterministic replay
    # --------------------------------------------------------

    results.append(
        test_deterministic_replay()
    )

    # --------------------------------------------------------
    # 14. Multi replay
    # --------------------------------------------------------

    results.append(
        test_multi_replay_stability(
            count=20
        )
    )

    # ========================================================
    # Final Summary
    # ========================================================

    print_header(
        "Struct3D v3.0"
    )

    print(
        "CANONICAL WORLD REGRESSION SUITE"
    )

    print()

    for result in results:

        print(
            "{:<42} {}".format(
                result.name + ":",
                "PASS"
                if result.passed
                else
                "FAIL"
            )
        )

    all_passed = all(
        result.passed
        for result in results
    )

    print()

    print(
        "Total tests:",
        len(results)
    )

    print(
        "Passed:",
        sum(
            result.passed
            for result in results
        )
    )

    print(
        "Failed:",
        sum(
            not result.passed
            for result in results
        )
    )

    print()

    if all_passed:

        print(
            "STATUS: PASS"
        )

    else:

        print(
            "STATUS: FAIL"
        )

    print("=" * 60)

    return 0 if all_passed else 1


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )