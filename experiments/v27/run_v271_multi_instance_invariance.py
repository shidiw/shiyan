import os
import sys
import hashlib
import pickle
import numpy as np

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from structure.unit import StructuralUnit
from structure.assembly import StructuralObjectAssembly
from structure.instance import StructuralInstanceBuilder


# ============================================================
# Rigid Transformations
# ============================================================

def rotation_matrix_x(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ], dtype=float)


def rotation_matrix_y(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ], dtype=float)


def rotation_matrix_z(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ], dtype=float)


def rotate(points, R):

    center = np.mean(
        points,
        axis=0
    )

    X = points - center

    return X @ R.T + center


def translate(points, t):

    return (
        points
        +
        np.asarray(
            t,
            dtype=float
        )
    )


# ============================================================
# Primitive Generation
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
# Units
# ============================================================

def build_units(points_list):

    units = []

    for i, points in enumerate(
        points_list
    ):

        unit = StructuralUnit(
            points,
            primitive="sphere",
            indices=np.arange(
                len(points),
                dtype=np.int32
            )
        )

        unit.energy = {
            "value":
                0.1 + 0.1 * i
        }

        units.append(
            unit
        )

    return units


# ============================================================
# Assembly
# ============================================================

def build_assembly(units):

    # --------------------------------------------------------
    # Object 0:
    #
    # unit 0 -- unit 1
    #
    # Object 1:
    #
    # unit 2 -- unit 3
    #
    # unit 4 remains independent.
    #
    # Therefore:
    #
    # Object 0 = [0, 1]
    # Object 1 = [2, 3]
    # Object 2 = [4]
    #
    # and consequently:
    #
    # Instances = 3
    # --------------------------------------------------------

    relations = [

        {
            "source": 0,
            "target": 1,
            "type": "connected",
            "confidence": 1.0
        },

        {
            "source": 2,
            "target": 3,
            "type": "connected",
            "confidence": 1.0
        }
    ]

    assembler = StructuralObjectAssembly(
        threshold=0.6
    )

    objects = assembler.build(
        units,
        relations
    )

    return objects


# ============================================================
# Instances
# ============================================================

def build_instances(units):

    objects = build_assembly(
        units
    )

    builder = StructuralInstanceBuilder()

    instances = builder.build(
        units,
        objects
    )

    return objects, instances


# ============================================================
# Canonical Signature
# ============================================================

def instance_signature(instance):

    return {
        "canonical":
            instance.canonical_signature()
    }


# ============================================================
# Hash
# ============================================================

def instance_hash(instance):

    signature = instance_signature(
        instance
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Statistics
# ============================================================

def statistics(
    objects,
    instances
):

    return {
        "objects":
            len(objects),

        "instances":
            len(instances),

        "object_parts":
            [
                len(obj.parts)
                for obj in objects
            ],

        "instance_points":
            [
                len(inst.points)
                for inst in instances
            ],

        "instance_primitives":
            [
                list(inst.primitives)
                for inst in instances
            ]
    }


# ============================================================
# Canonical Ordering
# ============================================================

def canonical_instance_list(
    instances
):

    records = []

    for inst in instances:

        records.append(
            {
                "signature":
                    instance_signature(inst),

                "hash":
                    instance_hash(inst)
            }
        )

    # --------------------------------------------------------
    # Instance IDs are implementation identifiers.
    #
    # For invariance we compare canonical content instead.
    # --------------------------------------------------------

    records.sort(
        key=lambda x: x["hash"]
    )

    return records


# ============================================================
# Comparison
# ============================================================

def compare(
    name,
    objects_a,
    instances_a,
    objects_b,
    instances_b
):

    print()
    print("-" * 60)
    print(name)
    print("-" * 60)

    stats_a = statistics(
        objects_a,
        instances_a
    )

    stats_b = statistics(
        objects_b,
        instances_b
    )

    print(
        "Objects A:",
        stats_a["objects"]
    )

    print(
        "Objects B:",
        stats_b["objects"]
    )

    print(
        "Instances A:",
        stats_a["instances"]
    )

    print(
        "Instances B:",
        stats_b["instances"]
    )

    print(
        "Object parts A:",
        stats_a["object_parts"]
    )

    print(
        "Object parts B:",
        stats_b["object_parts"]
    )

    print(
        "Instance points A:",
        stats_a["instance_points"]
    )

    print(
        "Instance points B:",
        stats_b["instance_points"]
    )

    canonical_a = canonical_instance_list(
        instances_a
    )

    canonical_b = canonical_instance_list(
        instances_b
    )

    signatures_a = [
        x["signature"]
        for x in canonical_a
    ]

    signatures_b = [
        x["signature"]
        for x in canonical_b
    ]

    hashes_a = [
        x["hash"]
        for x in canonical_a
    ]

    hashes_b = [
        x["hash"]
        for x in canonical_b
    ]

    structure_equal = (
        stats_a["objects"]
        ==
        stats_b["objects"]
        and
        stats_a["instances"]
        ==
        stats_b["instances"]
        and
        stats_a["object_parts"]
        ==
        stats_b["object_parts"]
    )

    canonical_equal = (
        signatures_a
        ==
        signatures_b
    )

    hash_equal = (
        hashes_a
        ==
        hashes_b
    )

    print(
        "Structural statistics equal:",
        structure_equal
    )

    print(
        "Canonical equal:",
        canonical_equal
    )

    print(
        "Hash A:",
        hashes_a
    )

    print(
        "Hash B:",
        hashes_b
    )

    print(
        "Hash equal:",
        hash_equal
    )

    passed = (
        structure_equal
        and canonical_equal
        and hash_equal
    )

    if passed:

        print(
            "[PASS]",
            name
        )

    else:

        print(
            "[FAIL]",
            name
        )

    return passed


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v2.7.1 "
        "Multi-Instance Invariance"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Base scene
    # --------------------------------------------------------

    base_points = [

        make_sphere(
            center=[0.0, 0.0, 0.0],
            radius=1.0,
            n=200,
            seed=10
        ),

        make_sphere(
            center=[2.5, 0.0, 0.0],
            radius=0.8,
            n=250,
            seed=20
        ),

        make_sphere(
            center=[6.0, 0.0, 0.0],
            radius=0.7,
            n=300,
            seed=30
        ),

        make_sphere(
            center=[8.0, 0.0, 0.0],
            radius=0.6,
            n=350,
            seed=40
        ),

        make_sphere(
            center=[12.0, 0.0, 0.0],
            radius=0.5,
            n=150,
            seed=50
        )
    ]

    # --------------------------------------------------------
    # Base
    # --------------------------------------------------------

    base_units = build_units(
        base_points
    )

    base_objects, base_instances = build_instances(
        base_units
    )

    print()
    print("[1] Base Scene")

    base_stats = statistics(
        base_objects,
        base_instances
    )

    print(
        "Objects:",
        base_stats["objects"]
    )

    print(
        "Instances:",
        base_stats["instances"]
    )

    print(
        "Object parts:",
        base_stats["object_parts"]
    )

    print(
        "Instance points:",
        base_stats["instance_points"]
    )

    print(
        "Instance primitives:",
        base_stats["instance_primitives"]
    )

    if (
        base_stats["objects"] != 3
        or
        base_stats["instances"] != 3
    ):

        raise RuntimeError(
            "Base scene is not genuinely multi-instance."
        )

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    translated_points = [

        translate(
            p,
            [20.0, -7.0, 4.0]
        )

        for p in base_points
    ]

    translated_units = build_units(
        translated_points
    )

    translated_objects, translated_instances = (
        build_instances(
            translated_units
        )
    )

    translation_ok = compare(
        "Translation Invariance",
        base_objects,
        base_instances,
        translated_objects,
        translated_instances
    )

    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

    R = (
        rotation_matrix_z(
            np.deg2rad(37.0)
        )
        @
        rotation_matrix_y(
            np.deg2rad(23.0)
        )
        @
        rotation_matrix_x(
            np.deg2rad(19.0)
        )
    )

    rotated_points = [

        rotate(
            p,
            R
        )

        for p in base_points
    ]

    rotated_units = build_units(
        rotated_points
    )

    rotated_objects, rotated_instances = (
        build_instances(
            rotated_units
        )
    )

    rotation_ok = compare(
        "Rotation Invariance",
        base_objects,
        base_instances,
        rotated_objects,
        rotated_instances
    )

    # --------------------------------------------------------
    # Rotation + Translation
    # --------------------------------------------------------

    rigid_points = [

        translate(
            rotate(
                p,
                R
            ),
            [15.0, -3.0, 8.0]
        )

        for p in base_points
    ]

    rigid_units = build_units(
        rigid_points
    )

    rigid_objects, rigid_instances = (
        build_instances(
            rigid_units
        )
    )

    rigid_ok = compare(
        "Rotation + Translation Invariance",
        base_objects,
        base_instances,
        rigid_objects,
        rigid_instances
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v2.7.1")
    print("MULTI-INSTANCE INVARIANCE")
    print("=" * 60)

    print(
        "Translation:",
        translation_ok
    )

    print(
        "Rotation:",
        rotation_ok
    )

    print(
        "Rotation + Translation:",
        rigid_ok
    )

    if (
        translation_ok
        and rotation_ok
        and rigid_ok
    ):

        print()
        print("STATUS: PASS")

    else:

        print()
        print("STATUS: FAIL")

        raise RuntimeError(
            "Multi-instance invariance validation failed."
        )


if __name__ == "__main__":

    main()
